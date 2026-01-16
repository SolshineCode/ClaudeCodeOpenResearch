"""
Experiment 2: Needle in Structure

An attention archaeology experiment that probes where models "look"
when searching for information in structured documents.

Unlike standard needle-in-haystack, this varies:
1. Position in document hierarchy (depth)
2. Structural context (headers, lists, nested blocks)
3. Distractor quality and placement
4. Target specificity (unique vs. ambiguous references)

Key Questions:
- Does hierarchical position affect retrieval accuracy?
- Do structural markers (headers, bullets) act as attention anchors?
- How do distractors at different structural levels interfere?
"""

import json
import random
import string
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NeedleConfig:
    """Configuration for a needle stimulus."""
    needle_content: str  # The information to find
    needle_key: str      # The retrieval key (what to ask about)
    needle_value: str    # The correct answer


@dataclass
class StructuralPosition:
    """Describes where something is placed in document structure."""
    depth: int           # Nesting depth (0 = top level)
    section_index: int   # Which section at this depth
    local_position: str  # 'start', 'middle', 'end' within section


@dataclass
class DistractorConfig:
    """Configuration for distractors."""
    num_distractors: int
    similarity_level: str  # 'none', 'low', 'medium', 'high'
    positions: List[StructuralPosition]


class NeedleInStructureGenerator:
    """
    Generates needle-in-structure stimuli.

    The "needle" is a key-value fact embedded in a structured document.
    The task is to retrieve the value given the key.
    """

    # Fact templates for generating needles
    FACT_TEMPLATES = [
        ("The access code for {context} is", "{code}", "access code for {context}"),
        ("Project {context} has a budget of", "${amount}", "budget of Project {context}"),
        ("The deadline for {context} is", "{date}", "deadline for {context}"),
        ("Contact person for {context} is", "{name}", "contact person for {context}"),
        ("The priority level of {context} is", "{priority}", "priority level of {context}"),
        ("Meeting room for {context} is", "Room {room}", "meeting room for {context}"),
        ("The status of {context} is", "{status}", "status of {context}"),
    ]

    FILLER_TOPICS = [
        "System Architecture", "Data Processing", "User Interface",
        "Security Protocols", "Performance Metrics", "Integration Points",
        "Testing Procedures", "Deployment Pipeline", "Monitoring Setup",
        "Backup Strategy", "Access Control", "Audit Logging"
    ]

    STATUSES = ["Active", "Pending", "Completed", "On Hold", "Cancelled"]
    PRIORITIES = ["Critical", "High", "Medium", "Low", "Optional"]
    NAMES = ["Alice Chen", "Bob Smith", "Carol Davis", "David Lee", "Eva Martinez"]

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

    def _generate_code(self) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def _generate_amount(self) -> str:
        return f"{random.randint(10, 999)},{random.randint(100, 999)}"

    def _generate_date(self) -> str:
        month = random.choice(['January', 'February', 'March', 'April', 'May', 'June',
                               'July', 'August', 'September', 'October', 'November', 'December'])
        day = random.randint(1, 28)
        year = random.randint(2024, 2026)
        return f"{month} {day}, {year}"

    def _generate_room(self) -> str:
        return f"{random.choice(['A', 'B', 'C', 'D'])}-{random.randint(100, 999)}"

    def _fill_template(self, template: Tuple[str, str, str], context: str) -> NeedleConfig:
        """Fill a fact template with concrete values."""
        prefix, value_template, query_template = template

        # Generate concrete value
        value = value_template.format(
            code=self._generate_code(),
            amount=self._generate_amount(),
            date=self._generate_date(),
            name=random.choice(self.NAMES),
            priority=random.choice(self.PRIORITIES),
            room=self._generate_room(),
            status=random.choice(self.STATUSES)
        )

        return NeedleConfig(
            needle_content=f"{prefix.format(context=context)} {value}.",
            needle_key=query_template.format(context=context),
            needle_value=value
        )

    def _generate_filler_paragraph(self, topic: str) -> str:
        """Generate a plausible filler paragraph."""
        sentences = [
            f"The {topic.lower()} component handles essential system functions.",
            f"Key considerations for {topic.lower()} include scalability and reliability.",
            f"Documentation for {topic.lower()} should be maintained regularly.",
            f"Team members should familiarize themselves with {topic.lower()} procedures.",
            f"Updates to {topic.lower()} follow the standard change management process.",
        ]
        return ' '.join(random.sample(sentences, k=random.randint(2, 4)))

    def _generate_distractor(self, needle: NeedleConfig, similarity: str) -> str:
        """Generate a distractor fact with specified similarity to needle."""
        if similarity == 'none':
            # Completely unrelated
            topic = random.choice(self.FILLER_TOPICS)
            return self._generate_filler_paragraph(topic)

        elif similarity == 'low':
            # Same structure but different key
            template = random.choice(self.FACT_TEMPLATES)
            context = f"Unrelated-{random.randint(1000, 9999)}"
            distractor = self._fill_template(template, context)
            return distractor.needle_content

        elif similarity == 'medium':
            # Similar key, different value
            # Modify the needle key slightly
            original_key = needle.needle_key
            modified_context = original_key.replace(
                original_key.split()[-1],
                f"Related-{random.randint(100, 999)}"
            )
            template = random.choice(self.FACT_TEMPLATES)
            distractor = self._fill_template(template, modified_context)
            return distractor.needle_content

        else:  # high
            # Very similar - same key pattern, plausible but wrong value
            words = needle.needle_content.split()
            # Change the value portion
            if '$' in needle.needle_value:
                new_value = f"${self._generate_amount()}"
            elif any(m in needle.needle_value for m in ['January', 'February', 'March']):
                new_value = self._generate_date()
            elif 'Room' in needle.needle_value:
                new_value = f"Room {self._generate_room()}"
            else:
                new_value = self._generate_code()

            # Create similar but wrong statement
            key_part = needle.needle_content.rsplit(' ', 1)[0]
            return f"{key_part} {new_value}. (Note: Verify this information)"

    def generate_structured_document(
        self,
        needle: NeedleConfig,
        needle_position: StructuralPosition,
        distractor_config: DistractorConfig,
        total_sections: int = 8,
        format: str = 'markdown'
    ) -> Dict:
        """
        Generate a structured document with embedded needle and distractors.

        Returns dict with:
            - document: The rendered document
            - needle: The needle configuration
            - needle_position: Where the needle was placed
            - distractors: List of distractor info
        """
        # Build document structure
        sections = []

        for i in range(total_sections):
            topic = self.FILLER_TOPICS[i % len(self.FILLER_TOPICS)]
            content = self._generate_filler_paragraph(topic)
            sections.append({
                'title': topic,
                'content': content,
                'subsections': []
            })

            # Add subsections
            num_subsections = random.randint(1, 3)
            for j in range(num_subsections):
                subtopic = f"{topic} - Part {j + 1}"
                subcontent = self._generate_filler_paragraph(subtopic)
                sections[i]['subsections'].append({
                    'title': subtopic,
                    'content': subcontent
                })

        # Place needle
        target_section = needle_position.section_index % len(sections)
        if needle_position.depth == 0:
            # Place in main section
            original = sections[target_section]['content']
            if needle_position.local_position == 'start':
                sections[target_section]['content'] = needle.needle_content + ' ' + original
            elif needle_position.local_position == 'end':
                sections[target_section]['content'] = original + ' ' + needle.needle_content
            else:  # middle
                words = original.split()
                mid = len(words) // 2
                sections[target_section]['content'] = ' '.join(
                    words[:mid] + [needle.needle_content] + words[mid:]
                )
        else:
            # Place in subsection
            subsections = sections[target_section]['subsections']
            if subsections:
                target_sub = needle_position.section_index % len(subsections)
                original = subsections[target_sub]['content']
                subsections[target_sub]['content'] = original + ' ' + needle.needle_content

        # Place distractors
        distractor_texts = []
        for i, pos in enumerate(distractor_config.positions):
            distractor = self._generate_distractor(needle, distractor_config.similarity_level)
            distractor_texts.append(distractor)

            target_section_idx = pos.section_index % len(sections)
            if pos.depth == 0:
                sections[target_section_idx]['content'] += ' ' + distractor
            else:
                subsections = sections[target_section_idx]['subsections']
                if subsections:
                    target_sub = pos.section_index % len(subsections)
                    subsections[target_sub]['content'] += ' ' + distractor

        # Render document
        document = self._render_document(sections, format)

        return {
            'document': document,
            'needle': {
                'content': needle.needle_content,
                'key': needle.needle_key,
                'value': needle.needle_value
            },
            'needle_position': {
                'depth': needle_position.depth,
                'section_index': target_section,
                'local_position': needle_position.local_position
            },
            'distractors': {
                'count': len(distractor_texts),
                'similarity': distractor_config.similarity_level,
                'texts': distractor_texts
            },
            'format': format
        }

    def _render_document(self, sections: List[Dict], format: str) -> str:
        """Render document structure to string."""
        if format == 'markdown':
            lines = ["# Technical Documentation\n"]
            for section in sections:
                lines.append(f"## {section['title']}\n")
                lines.append(section['content'] + "\n")
                for sub in section['subsections']:
                    lines.append(f"### {sub['title']}\n")
                    lines.append(sub['content'] + "\n")
            return '\n'.join(lines)

        elif format == 'xml':
            lines = ['<?xml version="1.0"?>', '<document title="Technical Documentation">']
            for section in sections:
                lines.append(f'  <section title="{section["title"]}">')
                lines.append(f'    <content>{section["content"]}</content>')
                for sub in section['subsections']:
                    lines.append(f'    <subsection title="{sub["title"]}">')
                    lines.append(f'      <content>{sub["content"]}</content>')
                    lines.append('    </subsection>')
                lines.append('  </section>')
            lines.append('</document>')
            return '\n'.join(lines)

        else:  # plain text with indentation
            lines = ["TECHNICAL DOCUMENTATION", "=" * 40, ""]
            for section in sections:
                lines.append(section['title'].upper())
                lines.append("-" * len(section['title']))
                lines.append(section['content'])
                lines.append("")
                for sub in section['subsections']:
                    lines.append(f"    {sub['title']}")
                    lines.append(f"    {'-' * len(sub['title'])}")
                    lines.append(f"    {sub['content']}")
                    lines.append("")
            return '\n'.join(lines)


def create_needle_probe(stimulus: Dict) -> Dict:
    """Create a probing question for a needle-in-structure stimulus."""
    return {
        'prompt': f"""Read the following document carefully, then answer the question.

## Document

{stimulus['document']}

## Question

What is the {stimulus['needle']['key']}?

## Instructions

Provide only the answer value, nothing else. If you cannot find the information, respond with "NOT FOUND".

Your answer:""",
        'expected_answer': stimulus['needle']['value'],
        'needle_position': stimulus['needle_position'],
        'distractor_info': stimulus['distractors'],
        'format': stimulus['format']
    }


def generate_experiment_suite(seed: int = 42) -> List[Dict]:
    """
    Generate a full experimental suite varying:
    - Needle depth (0, 1)
    - Needle position (start, middle, end)
    - Distractor similarity (none, low, medium, high)
    - Document format (markdown, xml, text)
    """
    generator = NeedleInStructureGenerator(seed=seed)

    trials = []
    trial_id = 0

    depths = [0, 1]
    positions = ['start', 'middle', 'end']
    similarities = ['none', 'low', 'medium', 'high']
    formats = ['markdown', 'xml', 'text']

    for depth in depths:
        for pos in positions:
            for sim in similarities:
                for fmt in formats:
                    # Generate needle
                    template = random.choice(generator.FACT_TEMPLATES)
                    context = f"Alpha-{trial_id:03d}"
                    needle = generator._fill_template(template, context)

                    # Configure position
                    needle_pos = StructuralPosition(
                        depth=depth,
                        section_index=random.randint(2, 5),  # Middle sections
                        local_position=pos
                    )

                    # Configure distractors
                    num_distractors = 3 if sim != 'none' else 0
                    distractor_positions = [
                        StructuralPosition(depth=d, section_index=s, local_position='end')
                        for d, s in [(0, 1), (1, 3), (0, 6)][:num_distractors]
                    ]
                    distractor_config = DistractorConfig(
                        num_distractors=num_distractors,
                        similarity_level=sim,
                        positions=distractor_positions
                    )

                    # Generate stimulus
                    stimulus = generator.generate_structured_document(
                        needle=needle,
                        needle_position=needle_pos,
                        distractor_config=distractor_config,
                        format=fmt
                    )

                    # Create probe
                    probe = create_needle_probe(stimulus)
                    probe['trial_id'] = f"NIS_{trial_id:04d}"
                    probe['conditions'] = {
                        'depth': depth,
                        'position': pos,
                        'distractor_similarity': sim,
                        'format': fmt
                    }

                    trials.append(probe)
                    trial_id += 1

    return trials


def create_experiment_protocol() -> Dict:
    """Create documented experiment protocol."""
    return {
        'experiment_name': 'Needle in Structure',
        'version': '1.0',
        'date_created': datetime.now().isoformat(),
        'description': '''
            Tests information retrieval from structured documents with varying:
            - Needle placement (depth and local position)
            - Distractor quality (similarity to target)
            - Document format

            This probes how structural context affects attention/retrieval.
        ''',
        'hypotheses': [
            'H1: Headers act as attention anchors - needles after headers easier to find',
            'H2: Deeper nesting reduces retrieval accuracy',
            'H3: High-similarity distractors cause more errors than low-similarity',
            'H4: Explicit structure (XML) aids retrieval vs implicit (plain text)',
            'H5: Position within section matters (start > end > middle)',
        ],
        'independent_variables': [
            {'name': 'needle_depth', 'levels': [0, 1], 'description': 'Nesting level of needle'},
            {'name': 'local_position', 'levels': ['start', 'middle', 'end'], 'description': 'Position within section'},
            {'name': 'distractor_similarity', 'levels': ['none', 'low', 'medium', 'high']},
            {'name': 'format', 'levels': ['markdown', 'xml', 'text']},
        ],
        'dependent_variables': [
            {'name': 'accuracy', 'type': 'binary'},
            {'name': 'response', 'type': 'string'},
            {'name': 'error_type', 'type': 'categorical', 'levels': ['correct', 'distractor', 'not_found', 'other']},
        ],
        'total_trials': 2 * 3 * 4 * 3,  # depth * position * similarity * format = 72
    }


if __name__ == '__main__':
    print("=" * 70)
    print("NEEDLE IN STRUCTURE EXPERIMENT - SAMPLE TRIALS")
    print("=" * 70)

    trials = generate_experiment_suite(seed=42)

    # Show a few sample trials
    for trial in trials[:3]:
        print(f"\n{'='*70}")
        print(f"Trial: {trial['trial_id']}")
        print(f"Conditions: {trial['conditions']}")
        print(f"Expected Answer: {trial['expected_answer']}")
        print(f"{'='*70}")
        print("\nPROMPT (truncated):")
        print(trial['prompt'][:1000] + "...")

    # Save protocol
    protocol = create_experiment_protocol()
    protocol_path = Path(__file__).parent.parent.parent / 'data' / 'stimuli'
    protocol_path.mkdir(parents=True, exist_ok=True)

    with open(protocol_path / 'needle_in_structure_protocol.json', 'w') as f:
        json.dump(protocol, f, indent=2)

    print(f"\n\nGenerated {len(trials)} trials")
    print(f"Protocol saved to: {protocol_path / 'needle_in_structure_protocol.json'}")
