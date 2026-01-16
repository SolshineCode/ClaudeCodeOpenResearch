"""
Experiment 4: Multi-Hop Document Reasoning

Tests reasoning that requires integrating information from multiple
locations in a structured document, following explicit or implicit
structural cues.

Key Questions:
- How does reasoning accuracy scale with number of hops?
- Do structural cues (cross-references) help or hinder?
- What's the interaction between hop count and document length?
- Can models follow different types of document links?
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReasoningChain:
    """Represents a multi-hop reasoning chain."""
    hops: List[Dict]  # Each hop: {location, fact, link_to_next}
    question: str
    answer: str
    chain_type: str  # 'explicit', 'implicit', 'mixed'


class MultiHopDocumentGenerator:
    """
    Generates documents with embedded multi-hop reasoning chains.

    Chain types:
    - Explicit: Clear cross-references ("See Section 3.2")
    - Implicit: Requires inference ("The primary server" -> find which is primary)
    - Mixed: Combination of explicit and implicit links
    """

    DOMAINS = {
        'organization': {
            'entities': ['Department', 'Team', 'Employee', 'Project', 'Resource'],
            'relations': ['reports_to', 'manages', 'works_on', 'owns', 'allocated_to'],
            'properties': ['budget', 'headcount', 'location', 'status', 'priority']
        },
        'technical': {
            'entities': ['Service', 'Database', 'API', 'Module', 'Config'],
            'relations': ['depends_on', 'calls', 'stores_in', 'configured_by', 'routes_to'],
            'properties': ['version', 'endpoint', 'port', 'timeout', 'retry_count']
        },
        'supply_chain': {
            'entities': ['Supplier', 'Product', 'Warehouse', 'Order', 'Shipment'],
            'relations': ['supplies', 'stored_in', 'contains', 'shipped_via', 'ordered_from'],
            'properties': ['quantity', 'price', 'location', 'eta', 'tracking_id']
        }
    }

    def __init__(self, seed: Optional[int] = None, domain: str = 'organization'):
        if seed is not None:
            random.seed(seed)
        self.domain = self.DOMAINS.get(domain, self.DOMAINS['organization'])

    def _generate_entity_id(self, entity_type: str, index: int) -> str:
        return f"{entity_type.lower()}_{index:03d}"

    def _generate_property_value(self, prop: str) -> str:
        if prop == 'budget':
            return f"${random.randint(10, 999)},{random.randint(100, 999)}"
        elif prop == 'headcount':
            return str(random.randint(5, 50))
        elif prop == 'location':
            return random.choice(['Building A', 'Building B', 'Building C', 'Remote'])
        elif prop == 'status':
            return random.choice(['Active', 'Planning', 'On Hold', 'Completed'])
        elif prop == 'priority':
            return random.choice(['P0', 'P1', 'P2', 'P3'])
        elif prop == 'version':
            return f"v{random.randint(1,5)}.{random.randint(0,9)}"
        elif prop == 'port':
            return str(random.randint(3000, 9000))
        elif prop == 'endpoint':
            return f"/api/v{random.randint(1,3)}/{random.choice(['data', 'auth', 'query'])}"
        elif prop in ['timeout', 'retry_count']:
            return str(random.randint(1, 10))
        elif prop == 'quantity':
            return str(random.randint(100, 10000))
        elif prop == 'price':
            return f"${random.randint(10, 999)}.{random.randint(10, 99)}"
        elif prop == 'eta':
            return f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        elif prop == 'tracking_id':
            return f"TRK{random.randint(100000, 999999)}"
        else:
            return f"value_{random.randint(1000, 9999)}"

    def generate_reasoning_chain(
        self,
        num_hops: int,
        chain_type: str = 'explicit'
    ) -> Tuple[Dict, ReasoningChain]:
        """
        Generate a document with an embedded reasoning chain.

        Returns (document_data, reasoning_chain)
        """
        # Generate entities
        entity_types = random.sample(self.domain['entities'], min(num_hops + 1, len(self.domain['entities'])))
        entities = []

        for i, etype in enumerate(entity_types):
            entity = {
                'id': self._generate_entity_id(etype, i),
                'name': f"{etype} {chr(65 + i)}",  # Entity A, Entity B, etc.
                'type': etype,
                'section_num': f"{i + 1}",
                'properties': {}
            }
            # Add random properties
            props = random.sample(self.domain['properties'], k=min(3, len(self.domain['properties'])))
            for prop in props:
                entity['properties'][prop] = self._generate_property_value(prop)
            entities.append(entity)

        # Build reasoning chain
        hops = []
        for i in range(num_hops):
            current = entities[i]
            next_entity = entities[i + 1] if i + 1 < len(entities) else None

            # Create link based on chain type
            if chain_type == 'explicit':
                link = f"(See Section {next_entity['section_num']})" if next_entity else None
            elif chain_type == 'implicit':
                link = f"managed by the {next_entity['type'].lower()}" if next_entity else None
            else:  # mixed
                if i % 2 == 0:
                    link = f"(Refer to {next_entity['name']})" if next_entity else None
                else:
                    link = f"overseen by {next_entity['name']}" if next_entity else None

            # The fact at this hop
            if next_entity:
                relation = random.choice(self.domain['relations'])
                fact = f"{current['name']} {relation.replace('_', ' ')} {next_entity['name']}"
            else:
                # Final hop - the answer
                target_prop = random.choice(list(current['properties'].keys()))
                fact = f"The {target_prop.replace('_', ' ')} is {current['properties'][target_prop]}"

            hops.append({
                'location': f"Section {current['section_num']}",
                'entity': current['name'],
                'fact': fact,
                'link_to_next': link
            })

        # The answer is a property of the final entity
        final_entity = entities[-1]
        target_prop = random.choice(list(final_entity['properties'].keys()))
        answer = final_entity['properties'][target_prop]

        # Generate question that requires following the chain
        first_entity = entities[0]
        question = f"Starting from {first_entity['name']}, follow the chain of relationships to find the {target_prop.replace('_', ' ')} of the final entity in the chain."

        chain = ReasoningChain(
            hops=hops,
            question=question,
            answer=answer,
            chain_type=chain_type
        )

        # Build document
        document = self._build_document(entities, chain)

        return document, chain

    def _build_document(self, entities: List[Dict], chain: ReasoningChain) -> Dict:
        """Build a document containing the entities and chain."""
        sections = []

        for i, entity in enumerate(entities):
            # Find relevant hop
            hop = chain.hops[i] if i < len(chain.hops) else None

            content_parts = [f"This section describes {entity['name']}."]

            # Add properties
            for prop, value in entity['properties'].items():
                content_parts.append(f"The {prop.replace('_', ' ')} is {value}.")

            # Add chain fact with link
            if hop:
                content_parts.append(hop['fact'] + ".")
                if hop['link_to_next']:
                    content_parts.append(hop['link_to_next'])

            sections.append({
                'number': entity['section_num'],
                'title': entity['name'],
                'entity_type': entity['type'],
                'content': ' '.join(content_parts)
            })

        return {
            'title': 'Entity Reference Document',
            'sections': sections,
            'entity_count': len(entities)
        }

    def render_markdown(self, document: Dict) -> str:
        """Render document as markdown."""
        lines = [f"# {document['title']}\n"]

        for section in document['sections']:
            lines.append(f"## Section {section['number']}: {section['title']}\n")
            lines.append(section['content'])
            lines.append("")

        return '\n'.join(lines)

    def render_structured(self, document: Dict) -> str:
        """Render document with explicit structure markers."""
        lines = [f"DOCUMENT: {document['title']}", "=" * 50, ""]

        for section in document['sections']:
            lines.append(f"[SECTION {section['number']}]")
            lines.append(f"TITLE: {section['title']}")
            lines.append(f"TYPE: {section['entity_type']}")
            lines.append(f"CONTENT: {section['content']}")
            lines.append("-" * 30)

        return '\n'.join(lines)


def create_multi_hop_trial(
    seed: int,
    num_hops: int,
    chain_type: str,
    format: str = 'markdown'
) -> Dict:
    """Create a single multi-hop reasoning trial."""
    generator = MultiHopDocumentGenerator(seed=seed)
    document, chain = generator.generate_reasoning_chain(num_hops, chain_type)

    if format == 'markdown':
        rendered = generator.render_markdown(document)
    else:
        rendered = generator.render_structured(document)

    # Build the reasoning trace (for analysis)
    trace = []
    for i, hop in enumerate(chain.hops):
        trace.append({
            'step': i + 1,
            'location': hop['location'],
            'fact_found': hop['fact'],
            'link_type': 'explicit' if '(See' in str(hop['link_to_next']) or '(Refer' in str(hop['link_to_next']) else 'implicit'
        })

    return {
        'trial_id': f"MH_{seed}_{num_hops}hop_{chain_type}",
        'prompt': f"""Read the following document carefully. You will need to follow a chain of relationships across multiple sections to answer the question.

## Document

{rendered}

## Question

{chain.question}

## Instructions

1. Start at the specified entity
2. Follow the relationships mentioned (look for cross-references or relationship statements)
3. Continue until you reach the final entity in the chain
4. Report the requested property value

Think through each step, then provide your final answer.

Your answer:""",
        'expected_answer': chain.answer,
        'num_hops': num_hops,
        'chain_type': chain_type,
        'format': format,
        'reasoning_trace': trace,
        'question': chain.question
    }


def generate_experiment_suite(seed_start: int = 5000) -> List[Dict]:
    """Generate full experiment suite varying hops, chain type, and format."""
    trials = []

    hop_counts = [2, 3, 4, 5]
    chain_types = ['explicit', 'implicit', 'mixed']
    formats = ['markdown', 'structured']

    trial_num = 0
    for hops in hop_counts:
        for chain_type in chain_types:
            for fmt in formats:
                # Multiple seeds per condition
                for rep in range(3):
                    trial = create_multi_hop_trial(
                        seed=seed_start + trial_num,
                        num_hops=hops,
                        chain_type=chain_type,
                        format=fmt
                    )
                    trials.append(trial)
                    trial_num += 1

    return trials


def analyze_error_patterns(results: List[Dict]) -> Dict:
    """
    Analyze error patterns in results.

    Expected result format: trial dict with added 'model_answer' and 'correct' fields
    """
    analysis = {
        'by_hops': {},
        'by_chain_type': {},
        'by_format': {},
        'error_types': {
            'partial_chain': 0,  # Stopped before reaching end
            'wrong_property': 0,  # Right entity, wrong property
            'hallucination': 0,  # Answer not in document
            'correct': 0
        }
    }

    for result in results:
        hops = result['num_hops']
        chain_type = result['chain_type']
        fmt = result['format']
        correct = result.get('correct', False)

        # Aggregate by condition
        for key, value, store in [
            ('by_hops', hops, analysis['by_hops']),
            ('by_chain_type', chain_type, analysis['by_chain_type']),
            ('by_format', fmt, analysis['by_format'])
        ]:
            if value not in store:
                store[value] = {'correct': 0, 'total': 0}
            store[value]['total'] += 1
            if correct:
                store[value]['correct'] += 1

        if correct:
            analysis['error_types']['correct'] += 1

    # Calculate accuracies
    for category in ['by_hops', 'by_chain_type', 'by_format']:
        for key in analysis[category]:
            data = analysis[category][key]
            data['accuracy'] = data['correct'] / data['total'] if data['total'] > 0 else 0

    return analysis


def create_experiment_protocol() -> Dict:
    """Create documented experiment protocol."""
    return {
        'experiment_name': 'Multi-Hop Document Reasoning',
        'version': '1.0',
        'date_created': datetime.now().isoformat(),
        'description': '''
            Tests multi-step reasoning through structured documents by
            embedding reasoning chains that require following relationships
            across multiple sections.
        ''',
        'hypotheses': [
            'H1: Accuracy decreases linearly (or worse) with hop count',
            'H2: Explicit cross-references yield higher accuracy than implicit',
            'H3: Structured format markers improve multi-hop performance',
            'H4: Error analysis will show most failures at early hops (chain breaks)',
            'H5: Mixed chains perform between explicit and implicit',
        ],
        'independent_variables': [
            {'name': 'num_hops', 'levels': [2, 3, 4, 5]},
            {'name': 'chain_type', 'levels': ['explicit', 'implicit', 'mixed']},
            {'name': 'format', 'levels': ['markdown', 'structured']},
        ],
        'dependent_variables': [
            {'name': 'accuracy', 'type': 'binary'},
            {'name': 'error_type', 'type': 'categorical'},
        ],
        'total_trials': 4 * 3 * 2 * 3,  # hops * types * formats * reps = 72
        'analysis_plan': '''
            1. Accuracy by hop count (test H1)
            2. Accuracy by chain type (test H2, H5)
            3. Accuracy by format (test H3)
            4. Error pattern analysis (test H4)
            5. Interaction: hops x chain_type
        '''
    }


if __name__ == '__main__':
    print("=" * 70)
    print("MULTI-HOP DOCUMENT REASONING - SAMPLE TRIALS")
    print("=" * 70)

    # Generate samples
    for hops in [2, 3, 4]:
        trial = create_multi_hop_trial(
            seed=42 + hops,
            num_hops=hops,
            chain_type='explicit',
            format='markdown'
        )

        print(f"\n{'='*70}")
        print(f"TRIAL: {hops}-hop, explicit, markdown")
        print(f"Expected Answer: {trial['expected_answer']}")
        print(f"{'='*70}")
        print("\nReasoning Trace:")
        for step in trial['reasoning_trace']:
            print(f"  Step {step['step']}: {step['location']} - {step['fact_found'][:50]}...")
        print(f"\n--- PROMPT (truncated) ---")
        print(trial['prompt'][:1200] + "...")

    # Save protocol
    protocol = create_experiment_protocol()
    protocol_path = Path(__file__).parent.parent.parent / 'data' / 'stimuli'
    protocol_path.mkdir(parents=True, exist_ok=True)

    with open(protocol_path / 'multi_hop_protocol.json', 'w') as f:
        json.dump(protocol, f, indent=2)

    print(f"\n\nProtocol saved to: {protocol_path / 'multi_hop_protocol.json'}")
