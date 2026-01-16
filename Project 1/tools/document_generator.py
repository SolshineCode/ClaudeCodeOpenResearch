"""
Document Generator for Interpretability Experiments

Generates structured documents with known ground truth properties
for probing LLM document understanding capabilities.
"""

import json
import random
import string
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict


@dataclass
class DocumentNode:
    """A node in a hierarchical document structure."""
    id: str
    content: str
    depth: int
    children: List['DocumentNode'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'content': self.content,
            'depth': self.depth,
            'children': [c.to_dict() for c in self.children],
            'metadata': self.metadata
        }


@dataclass
class GroundTruth:
    """Ground truth facts about a generated document."""
    total_nodes: int
    max_depth: int
    node_at_depth: Dict[int, List[str]]  # depth -> list of node IDs
    parent_child_pairs: List[Tuple[str, str]]  # (parent_id, child_id)
    sibling_pairs: List[Tuple[str, str]]  # (node_id, sibling_id)
    leaf_nodes: List[str]
    root_nodes: List[str]
    path_to_node: Dict[str, List[str]]  # node_id -> path from root

    def to_dict(self) -> Dict:
        return asdict(self)


class HierarchicalDocumentGenerator:
    """Generates hierarchical documents with controlled properties."""

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.word_bank = self._create_word_bank()

    def _create_word_bank(self) -> Dict[str, List[str]]:
        """Create categorized word bank for content generation."""
        return {
            'topics': [
                'Architecture', 'Systems', 'Protocols', 'Methods',
                'Frameworks', 'Patterns', 'Structures', 'Processes',
                'Components', 'Interfaces', 'Modules', 'Services',
                'Algorithms', 'Strategies', 'Policies', 'Guidelines'
            ],
            'adjectives': [
                'Primary', 'Secondary', 'Core', 'Extended',
                'Basic', 'Advanced', 'Standard', 'Custom',
                'Internal', 'External', 'Local', 'Global',
                'Static', 'Dynamic', 'Reactive', 'Proactive'
            ],
            'actions': [
                'Configuration', 'Implementation', 'Integration', 'Optimization',
                'Validation', 'Processing', 'Management', 'Coordination',
                'Execution', 'Initialization', 'Termination', 'Monitoring'
            ]
        }

    def _generate_id(self, prefix: str = 'node') -> str:
        """Generate unique node ID."""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{prefix}_{suffix}"

    def _generate_content(self, depth: int, index: int) -> str:
        """Generate plausible content for a node."""
        adj = random.choice(self.word_bank['adjectives'])
        topic = random.choice(self.word_bank['topics'])
        action = random.choice(self.word_bank['actions'])
        return f"{adj} {topic} {action} (Level {depth}, Item {index})"

    def generate_tree(
        self,
        max_depth: int = 3,
        branching_factor: Tuple[int, int] = (2, 4),
        content_generator: Optional[callable] = None
    ) -> Tuple[DocumentNode, GroundTruth]:
        """
        Generate a hierarchical document tree.

        Args:
            max_depth: Maximum nesting depth (0 = root only)
            branching_factor: (min, max) children per node
            content_generator: Optional custom content generator

        Returns:
            Tuple of (root_node, ground_truth)
        """
        ground_truth_data = {
            'total_nodes': 0,
            'max_depth': 0,
            'node_at_depth': {},
            'parent_child_pairs': [],
            'sibling_pairs': [],
            'leaf_nodes': [],
            'root_nodes': [],
            'path_to_node': {}
        }

        def build_subtree(depth: int, path: List[str]) -> DocumentNode:
            node_id = self._generate_id()
            content = (content_generator(depth, ground_truth_data['total_nodes'])
                      if content_generator
                      else self._generate_content(depth, ground_truth_data['total_nodes']))

            node = DocumentNode(
                id=node_id,
                content=content,
                depth=depth,
                metadata={'creation_order': ground_truth_data['total_nodes']}
            )

            # Update ground truth
            ground_truth_data['total_nodes'] += 1
            ground_truth_data['max_depth'] = max(ground_truth_data['max_depth'], depth)

            if depth not in ground_truth_data['node_at_depth']:
                ground_truth_data['node_at_depth'][depth] = []
            ground_truth_data['node_at_depth'][depth].append(node_id)

            current_path = path + [node_id]
            ground_truth_data['path_to_node'][node_id] = current_path

            if depth == 0:
                ground_truth_data['root_nodes'].append(node_id)

            # Generate children if not at max depth
            if depth < max_depth:
                num_children = random.randint(*branching_factor)
                child_ids = []

                for i in range(num_children):
                    child = build_subtree(depth + 1, current_path)
                    node.children.append(child)
                    ground_truth_data['parent_child_pairs'].append((node_id, child.id))
                    child_ids.append(child.id)

                # Record sibling relationships
                for i, cid in enumerate(child_ids):
                    for j, other_cid in enumerate(child_ids):
                        if i != j:
                            ground_truth_data['sibling_pairs'].append((cid, other_cid))

            if not node.children:
                ground_truth_data['leaf_nodes'].append(node_id)

            return node

        root = build_subtree(0, [])
        ground_truth = GroundTruth(**ground_truth_data)

        return root, ground_truth


class DocumentRenderer:
    """Renders document trees to various formats."""

    @staticmethod
    def to_markdown(node: DocumentNode, include_ids: bool = True) -> str:
        """Render document tree as markdown."""
        lines = []

        def render_node(n: DocumentNode, level: int = 1):
            prefix = '#' * min(level, 6)
            id_suffix = f" [{n.id}]" if include_ids else ""
            lines.append(f"{prefix} {n.content}{id_suffix}")
            lines.append("")
            for child in n.children:
                render_node(child, level + 1)

        render_node(node)
        return '\n'.join(lines)

    @staticmethod
    def to_json(node: DocumentNode, pretty: bool = True) -> str:
        """Render document tree as JSON."""
        indent = 2 if pretty else None
        return json.dumps(node.to_dict(), indent=indent)

    @staticmethod
    def to_xml(node: DocumentNode, include_ids: bool = True) -> str:
        """Render document tree as XML."""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']

        def render_node(n: DocumentNode, indent: int = 0):
            spaces = '  ' * indent
            id_attr = f' id="{n.id}"' if include_ids else ""
            depth_attr = f' depth="{n.depth}"'

            if n.children:
                lines.append(f'{spaces}<section{id_attr}{depth_attr}>')
                lines.append(f'{spaces}  <title>{n.content}</title>')
                for child in n.children:
                    render_node(child, indent + 1)
                lines.append(f'{spaces}</section>')
            else:
                lines.append(f'{spaces}<section{id_attr}{depth_attr}>')
                lines.append(f'{spaces}  <title>{n.content}</title>')
                lines.append(f'{spaces}</section>')

        render_node(node)
        return '\n'.join(lines)

    @staticmethod
    def to_indented_text(node: DocumentNode, include_ids: bool = True) -> str:
        """Render document tree as indented plain text."""
        lines = []

        def render_node(n: DocumentNode, indent: int = 0):
            spaces = '    ' * indent
            id_suffix = f" [{n.id}]" if include_ids else ""
            bullet = '•' if indent > 0 else '◆'
            lines.append(f"{spaces}{bullet} {n.content}{id_suffix}")
            for child in n.children:
                render_node(child, indent + 1)

        render_node(node)
        return '\n'.join(lines)


class ProbeGenerator:
    """Generates probing questions with ground truth answers."""

    @staticmethod
    def depth_probe(ground_truth: GroundTruth) -> Dict:
        """Generate a probe about node depths."""
        # Pick a random node
        all_nodes = []
        for depth, nodes in ground_truth.node_at_depth.items():
            for node_id in nodes:
                all_nodes.append((node_id, depth))

        target_id, target_depth = random.choice(all_nodes)

        return {
            'type': 'depth_probe',
            'question': f"What is the depth level of the section with ID [{target_id}]? (Root = 0)",
            'answer': target_depth,
            'target_node': target_id
        }

    @staticmethod
    def parent_probe(ground_truth: GroundTruth) -> Optional[Dict]:
        """Generate a probe about parent relationships."""
        if not ground_truth.parent_child_pairs:
            return None

        parent_id, child_id = random.choice(ground_truth.parent_child_pairs)

        return {
            'type': 'parent_probe',
            'question': f"What is the ID of the parent section of [{child_id}]?",
            'answer': parent_id,
            'target_node': child_id
        }

    @staticmethod
    def sibling_probe(ground_truth: GroundTruth) -> Optional[Dict]:
        """Generate a probe about sibling relationships."""
        if not ground_truth.sibling_pairs:
            return None

        node_id, sibling_id = random.choice(ground_truth.sibling_pairs)

        # Get all siblings of this node
        all_siblings = [s for n, s in ground_truth.sibling_pairs if n == node_id]

        return {
            'type': 'sibling_probe',
            'question': f"List all sibling sections of [{node_id}] (sections at the same level with the same parent).",
            'answer': all_siblings,
            'target_node': node_id
        }

    @staticmethod
    def leaf_probe(ground_truth: GroundTruth) -> Dict:
        """Generate a probe about leaf nodes."""
        target = random.choice(ground_truth.leaf_nodes)

        return {
            'type': 'leaf_probe',
            'question': f"Does the section [{target}] have any child sections? Answer yes or no.",
            'answer': 'no',
            'target_node': target
        }

    @staticmethod
    def path_probe(ground_truth: GroundTruth) -> Dict:
        """Generate a probe about paths from root."""
        # Pick a node that's not the root
        deep_nodes = [(nid, path) for nid, path in ground_truth.path_to_node.items()
                      if len(path) > 1]

        if not deep_nodes:
            # Only root exists
            root_id = ground_truth.root_nodes[0]
            return {
                'type': 'path_probe',
                'question': f"What is the path from the root to [{root_id}]?",
                'answer': [root_id],
                'target_node': root_id
            }

        target_id, path = random.choice(deep_nodes)

        return {
            'type': 'path_probe',
            'question': f"List the section IDs in order from the root to [{target_id}], including both endpoints.",
            'answer': path,
            'target_node': target_id
        }

    @staticmethod
    def count_probe(ground_truth: GroundTruth) -> Dict:
        """Generate a probe about counting nodes."""
        probe_type = random.choice(['total', 'at_depth', 'leaves'])

        if probe_type == 'total':
            return {
                'type': 'count_probe',
                'question': "How many total sections are in this document?",
                'answer': ground_truth.total_nodes,
                'subtype': 'total'
            }
        elif probe_type == 'at_depth':
            depth = random.choice(list(ground_truth.node_at_depth.keys()))
            count = len(ground_truth.node_at_depth[depth])
            return {
                'type': 'count_probe',
                'question': f"How many sections are at depth level {depth}?",
                'answer': count,
                'subtype': 'at_depth',
                'depth': depth
            }
        else:
            return {
                'type': 'count_probe',
                'question': "How many leaf sections (sections with no children) are in this document?",
                'answer': len(ground_truth.leaf_nodes),
                'subtype': 'leaves'
            }


def generate_experiment_stimulus(
    seed: int,
    max_depth: int = 3,
    branching: Tuple[int, int] = (2, 3),
    format: str = 'markdown',
    num_probes: int = 5
) -> Dict:
    """
    Generate a complete experimental stimulus with document and probes.

    Returns dict with:
        - document: Rendered document string
        - format: Format used
        - ground_truth: Full ground truth data
        - probes: List of probing questions with answers
    """
    generator = HierarchicalDocumentGenerator(seed=seed)
    root, ground_truth = generator.generate_tree(max_depth=max_depth, branching_factor=branching)

    # Render in requested format
    renderer = DocumentRenderer()
    format_map = {
        'markdown': renderer.to_markdown,
        'json': renderer.to_json,
        'xml': renderer.to_xml,
        'text': renderer.to_indented_text
    }
    document = format_map.get(format, renderer.to_markdown)(root)

    # Generate probes
    probe_gen = ProbeGenerator()
    probe_functions = [
        probe_gen.depth_probe,
        probe_gen.parent_probe,
        probe_gen.sibling_probe,
        probe_gen.leaf_probe,
        probe_gen.path_probe,
        probe_gen.count_probe
    ]

    probes = []
    for _ in range(num_probes):
        probe_fn = random.choice(probe_functions)
        probe = probe_fn(ground_truth)
        if probe is not None:
            probes.append(probe)

    return {
        'seed': seed,
        'document': document,
        'format': format,
        'ground_truth': ground_truth.to_dict(),
        'probes': probes,
        'tree': root.to_dict()
    }


if __name__ == '__main__':
    # Demo: Generate a sample stimulus
    stimulus = generate_experiment_stimulus(
        seed=42,
        max_depth=2,
        branching=(2, 3),
        format='markdown',
        num_probes=5
    )

    print("=" * 60)
    print("GENERATED DOCUMENT")
    print("=" * 60)
    print(stimulus['document'])
    print("\n" + "=" * 60)
    print("PROBING QUESTIONS")
    print("=" * 60)
    for i, probe in enumerate(stimulus['probes'], 1):
        print(f"\n{i}. [{probe['type']}]")
        print(f"   Q: {probe['question']}")
        print(f"   A: {probe['answer']}")
