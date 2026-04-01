"""
Experiment 3: Isomorphic Content Analysis

Tests how document format affects LLM processing of semantically
identical information. The same content is rendered in different
formats to isolate format-specific processing effects.

Key Questions:
- Do some formats enable better reasoning than others?
- What format-specific affordances exist?
- How robust is understanding to format perturbations?
- Can models transfer knowledge across formats?
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SemanticContent:
    """Format-independent semantic content."""
    entities: List[Dict]  # List of entity dicts with properties
    relations: List[Tuple[str, str, str]]  # (subject, predicate, object)
    facts: List[Dict]  # Key-value facts


class IsomorphicContentGenerator:
    """
    Generates semantically identical content in multiple formats.

    The same underlying information is rendered as:
    - Markdown (prose and tables)
    - JSON (nested objects)
    - XML (hierarchical elements)
    - YAML (configuration style)
    - Plain text (natural language)
    - CSV (tabular)
    """

    ENTITY_TYPES = ['Server', 'Database', 'Service', 'Endpoint', 'Module']
    PROPERTIES = ['status', 'version', 'port', 'memory_gb', 'cpu_cores', 'region']
    RELATION_TYPES = ['connects_to', 'depends_on', 'managed_by', 'replicated_to']
    REGIONS = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-northeast-1']
    STATUSES = ['active', 'standby', 'maintenance', 'degraded']

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

    def generate_semantic_content(self, num_entities: int = 5) -> SemanticContent:
        """Generate random but consistent semantic content."""
        entities = []
        for i in range(num_entities):
            entity_type = random.choice(self.ENTITY_TYPES)
            entity = {
                'id': f"{entity_type.lower()}_{i+1:02d}",
                'name': f"{entity_type} {chr(65+i)}",  # Server A, Server B, etc.
                'type': entity_type,
                'properties': {
                    'status': random.choice(self.STATUSES),
                    'version': f"{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,99)}",
                    'port': random.randint(3000, 9999),
                    'memory_gb': random.choice([4, 8, 16, 32, 64]),
                    'cpu_cores': random.choice([2, 4, 8, 16]),
                    'region': random.choice(self.REGIONS)
                }
            }
            entities.append(entity)

        # Generate relations between entities
        relations = []
        for i, entity in enumerate(entities[:-1]):
            target = random.choice(entities[i+1:])
            relation = random.choice(self.RELATION_TYPES)
            relations.append((entity['id'], relation, target['id']))

        # Generate some aggregate facts
        facts = [
            {'key': 'total_entities', 'value': num_entities},
            {'key': 'total_memory_gb', 'value': sum(e['properties']['memory_gb'] for e in entities)},
            {'key': 'total_cpu_cores', 'value': sum(e['properties']['cpu_cores'] for e in entities)},
            {'key': 'active_count', 'value': sum(1 for e in entities if e['properties']['status'] == 'active')},
            {'key': 'regions_used', 'value': list(set(e['properties']['region'] for e in entities))},
        ]

        return SemanticContent(entities=entities, relations=relations, facts=facts)

    def render_markdown_prose(self, content: SemanticContent) -> str:
        """Render as markdown with prose descriptions."""
        lines = ["# Infrastructure Overview\n"]

        lines.append("## Entities\n")
        for entity in content.entities:
            props = entity['properties']
            lines.append(f"### {entity['name']}\n")
            lines.append(f"**{entity['name']}** (ID: `{entity['id']}`) is a {entity['type'].lower()} "
                        f"currently in **{props['status']}** status. It runs version {props['version']} "
                        f"on port {props['port']}, with {props['memory_gb']}GB memory and "
                        f"{props['cpu_cores']} CPU cores, deployed in {props['region']}.\n")

        lines.append("## Relationships\n")
        for subj, pred, obj in content.relations:
            pred_readable = pred.replace('_', ' ')
            lines.append(f"- `{subj}` {pred_readable} `{obj}`")

        lines.append("\n## Summary Statistics\n")
        for fact in content.facts:
            key_readable = fact['key'].replace('_', ' ').title()
            value = fact['value']
            if isinstance(value, list):
                value = ', '.join(value)
            lines.append(f"- **{key_readable}**: {value}")

        return '\n'.join(lines)

    def render_markdown_table(self, content: SemanticContent) -> str:
        """Render as markdown with tables."""
        lines = ["# Infrastructure Overview\n"]

        lines.append("## Entities\n")
        lines.append("| ID | Name | Type | Status | Version | Port | Memory (GB) | CPU Cores | Region |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for entity in content.entities:
            props = entity['properties']
            lines.append(f"| {entity['id']} | {entity['name']} | {entity['type']} | "
                        f"{props['status']} | {props['version']} | {props['port']} | "
                        f"{props['memory_gb']} | {props['cpu_cores']} | {props['region']} |")

        lines.append("\n## Relationships\n")
        lines.append("| Subject | Relation | Object |")
        lines.append("|---|---|---|")
        for subj, pred, obj in content.relations:
            lines.append(f"| {subj} | {pred} | {obj} |")

        lines.append("\n## Summary\n")
        for fact in content.facts:
            value = fact['value']
            if isinstance(value, list):
                value = ', '.join(value)
            lines.append(f"- {fact['key']}: {value}")

        return '\n'.join(lines)

    def render_json(self, content: SemanticContent) -> str:
        """Render as JSON."""
        data = {
            'infrastructure': {
                'entities': {e['id']: {
                    'name': e['name'],
                    'type': e['type'],
                    **e['properties']
                } for e in content.entities},
                'relationships': [
                    {'from': s, 'type': p, 'to': o}
                    for s, p, o in content.relations
                ],
                'summary': {f['key']: f['value'] for f in content.facts}
            }
        }
        return json.dumps(data, indent=2)

    def render_xml(self, content: SemanticContent) -> str:
        """Render as XML."""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<infrastructure>']

        lines.append('  <entities>')
        for entity in content.entities:
            props = entity['properties']
            lines.append(f'    <entity id="{entity["id"]}" type="{entity["type"]}">')
            lines.append(f'      <name>{entity["name"]}</name>')
            for key, value in props.items():
                lines.append(f'      <{key}>{value}</{key}>')
            lines.append('    </entity>')
        lines.append('  </entities>')

        lines.append('  <relationships>')
        for subj, pred, obj in content.relations:
            lines.append(f'    <relation type="{pred}">')
            lines.append(f'      <from>{subj}</from>')
            lines.append(f'      <to>{obj}</to>')
            lines.append('    </relation>')
        lines.append('  </relationships>')

        lines.append('  <summary>')
        for fact in content.facts:
            value = fact['value']
            if isinstance(value, list):
                value = ','.join(value)
            lines.append(f'    <{fact["key"]}>{value}</{fact["key"]}>')
        lines.append('  </summary>')

        lines.append('</infrastructure>')
        return '\n'.join(lines)

    def render_yaml(self, content: SemanticContent) -> str:
        """Render as YAML."""
        lines = ['infrastructure:']

        lines.append('  entities:')
        for entity in content.entities:
            lines.append(f'    {entity["id"]}:')
            lines.append(f'      name: "{entity["name"]}"')
            lines.append(f'      type: {entity["type"]}')
            for key, value in entity['properties'].items():
                lines.append(f'      {key}: {value}')

        lines.append('  relationships:')
        for subj, pred, obj in content.relations:
            lines.append(f'    - from: {subj}')
            lines.append(f'      type: {pred}')
            lines.append(f'      to: {obj}')

        lines.append('  summary:')
        for fact in content.facts:
            value = fact['value']
            if isinstance(value, list):
                value = '[' + ', '.join(value) + ']'
            lines.append(f'    {fact["key"]}: {value}')

        return '\n'.join(lines)

    def render_plain_text(self, content: SemanticContent) -> str:
        """Render as plain natural language text."""
        lines = ["INFRASTRUCTURE OVERVIEW", "=" * 40, ""]

        lines.append("ENTITIES:")
        for entity in content.entities:
            props = entity['properties']
            lines.append(f"  {entity['name']} (ID: {entity['id']})")
            lines.append(f"    Type: {entity['type']}")
            lines.append(f"    Status: {props['status']}")
            lines.append(f"    Version: {props['version']}")
            lines.append(f"    Port: {props['port']}")
            lines.append(f"    Memory: {props['memory_gb']} GB")
            lines.append(f"    CPU Cores: {props['cpu_cores']}")
            lines.append(f"    Region: {props['region']}")
            lines.append("")

        lines.append("RELATIONSHIPS:")
        for subj, pred, obj in content.relations:
            lines.append(f"  {subj} --> [{pred}] --> {obj}")

        lines.append("")
        lines.append("SUMMARY:")
        for fact in content.facts:
            value = fact['value']
            if isinstance(value, list):
                value = ', '.join(value)
            lines.append(f"  {fact['key'].replace('_', ' ').title()}: {value}")

        return '\n'.join(lines)

    def render_csv(self, content: SemanticContent) -> str:
        """Render entity data as CSV."""
        lines = ["id,name,type,status,version,port,memory_gb,cpu_cores,region"]
        for entity in content.entities:
            props = entity['properties']
            lines.append(f"{entity['id']},{entity['name']},{entity['type']},"
                        f"{props['status']},{props['version']},{props['port']},"
                        f"{props['memory_gb']},{props['cpu_cores']},{props['region']}")
        return '\n'.join(lines)


class IsomorphicProbeGenerator:
    """Generates probes that test understanding across formats."""

    @staticmethod
    def entity_property_probe(content: SemanticContent) -> Dict:
        """Ask about a specific entity property."""
        entity = random.choice(content.entities)
        prop = random.choice(list(entity['properties'].keys()))
        return {
            'type': 'entity_property',
            'question': f"What is the {prop.replace('_', ' ')} of {entity['name']}?",
            'answer': str(entity['properties'][prop]),
            'target_entity': entity['id'],
            'target_property': prop
        }

    @staticmethod
    def relation_probe(content: SemanticContent) -> Dict:
        """Ask about relationships."""
        if not content.relations:
            return None
        subj, pred, obj = random.choice(content.relations)

        # Find entity names
        entities = {e['id']: e['name'] for e in content.entities}

        return {
            'type': 'relation',
            'question': f"What does {entities.get(subj, subj)} {pred.replace('_', ' ')}?",
            'answer': entities.get(obj, obj),
            'relation': (subj, pred, obj)
        }

    @staticmethod
    def aggregate_probe(content: SemanticContent) -> Dict:
        """Ask about aggregate facts."""
        fact = random.choice(content.facts)
        value = fact['value']
        if isinstance(value, list):
            value = ', '.join(sorted(value))

        return {
            'type': 'aggregate',
            'question': f"What is the {fact['key'].replace('_', ' ')}?",
            'answer': str(value),
            'fact_key': fact['key']
        }

    @staticmethod
    def comparison_probe(content: SemanticContent) -> Dict:
        """Ask to compare entities."""
        if len(content.entities) < 2:
            return None

        e1, e2 = random.sample(content.entities, 2)
        prop = random.choice(['memory_gb', 'cpu_cores', 'port'])

        v1 = e1['properties'][prop]
        v2 = e2['properties'][prop]

        if v1 > v2:
            answer = e1['name']
        elif v2 > v1:
            answer = e2['name']
        else:
            answer = "equal"

        return {
            'type': 'comparison',
            'question': f"Which has more {prop.replace('_', ' ')}: {e1['name']} or {e2['name']}?",
            'answer': answer,
            'entities': [e1['id'], e2['id']],
            'property': prop
        }

    @staticmethod
    def count_with_filter_probe(content: SemanticContent) -> Dict:
        """Ask to count entities matching a criterion."""
        # Pick a filterable property
        prop = random.choice(['status', 'region'])
        values = [e['properties'][prop] for e in content.entities]
        target_value = random.choice(values)

        count = sum(1 for e in content.entities if e['properties'][prop] == target_value)

        return {
            'type': 'count_filter',
            'question': f"How many entities have {prop} = {target_value}?",
            'answer': str(count),
            'filter_property': prop,
            'filter_value': target_value
        }


def generate_isomorphic_stimulus(seed: int, num_entities: int = 5) -> Dict:
    """Generate a complete isomorphic stimulus set."""
    generator = IsomorphicContentGenerator(seed=seed)
    content = generator.generate_semantic_content(num_entities)

    # Render in all formats
    formats = {
        'markdown_prose': generator.render_markdown_prose(content),
        'markdown_table': generator.render_markdown_table(content),
        'json': generator.render_json(content),
        'xml': generator.render_xml(content),
        'yaml': generator.render_yaml(content),
        'plain_text': generator.render_plain_text(content),
        'csv': generator.render_csv(content),
    }

    # Generate probes
    probe_gen = IsomorphicProbeGenerator()
    probes = [
        probe_gen.entity_property_probe(content),
        probe_gen.relation_probe(content),
        probe_gen.aggregate_probe(content),
        probe_gen.comparison_probe(content),
        probe_gen.count_with_filter_probe(content),
    ]
    probes = [p for p in probes if p is not None]

    return {
        'seed': seed,
        'content': {
            'entities': content.entities,
            'relations': content.relations,
            'facts': content.facts
        },
        'formats': formats,
        'probes': probes
    }


def create_format_comparison_trial(stimulus: Dict, format_name: str, probe: Dict) -> Dict:
    """Create a single trial for format comparison."""
    return {
        'prompt': f"""Analyze the following data and answer the question.

## Data ({format_name.replace('_', ' ').title()})

{stimulus['formats'][format_name]}

## Question

{probe['question']}

## Instructions

Provide only the answer, nothing else.

Your answer:""",
        'format': format_name,
        'probe': probe,
        'seed': stimulus['seed']
    }


def generate_experiment_suite(num_stimuli: int = 10, seed_start: int = 1000) -> List[Dict]:
    """Generate full experiment suite."""
    trials = []

    for i in range(num_stimuli):
        stimulus = generate_isomorphic_stimulus(seed=seed_start + i)

        for format_name in stimulus['formats'].keys():
            for probe in stimulus['probes']:
                trial = create_format_comparison_trial(stimulus, format_name, probe)
                trial['trial_id'] = f"ISO_{i:03d}_{format_name}_{probe['type']}"
                trials.append(trial)

    return trials


def create_experiment_protocol() -> Dict:
    """Create documented experiment protocol."""
    return {
        'experiment_name': 'Isomorphic Content Analysis',
        'version': '1.0',
        'date_created': datetime.now().isoformat(),
        'description': '''
            Tests how document format affects LLM understanding of semantically
            identical information. Same content rendered in 7 different formats
            with identical probing questions to isolate format effects.
        ''',
        'hypotheses': [
            'H1: Structured formats (JSON, XML) yield higher accuracy on property lookups',
            'H2: Tabular formats (CSV, MD tables) excel at comparison tasks',
            'H3: Prose formats better for relationship questions',
            'H4: Aggregate questions should be format-invariant',
            'H5: Count-with-filter tasks favor explicit structure',
        ],
        'formats_tested': [
            'markdown_prose', 'markdown_table', 'json',
            'xml', 'yaml', 'plain_text', 'csv'
        ],
        'probe_types': [
            'entity_property', 'relation', 'aggregate',
            'comparison', 'count_filter'
        ],
        'design': 'Within-subject: same content, all formats, same probes',
    }


if __name__ == '__main__':
    print("=" * 70)
    print("ISOMORPHIC CONTENT ANALYSIS - SAMPLE")
    print("=" * 70)

    stimulus = generate_isomorphic_stimulus(seed=42, num_entities=4)

    print("\n--- MARKDOWN PROSE ---")
    print(stimulus['formats']['markdown_prose'][:800] + "...\n")

    print("\n--- JSON ---")
    print(stimulus['formats']['json'][:800] + "...\n")

    print("\n--- PROBES ---")
    for probe in stimulus['probes']:
        print(f"  [{probe['type']}] {probe['question']}")
        print(f"    Answer: {probe['answer']}\n")

    # Save protocol
    protocol = create_experiment_protocol()
    protocol_path = Path(__file__).parent.parent.parent / 'data' / 'stimuli'
    protocol_path.mkdir(parents=True, exist_ok=True)

    with open(protocol_path / 'isomorphic_content_protocol.json', 'w') as f:
        json.dump(protocol, f, indent=2)

    print(f"\nProtocol saved to: {protocol_path / 'isomorphic_content_protocol.json'}")
