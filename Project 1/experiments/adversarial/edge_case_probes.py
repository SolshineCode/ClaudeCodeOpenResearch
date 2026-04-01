"""
Adversarial Edge Case Probes

Experiments designed to expose failure modes and edge cases in
document understanding. These probes target known or suspected
weaknesses in LLM document processing.

Categories:
1. Structural Ambiguity - Documents with unclear hierarchy
2. Semantic Interference - Similar content that could confuse
3. Positional Traps - Exploiting positional biases
4. Format Breaking - Edge cases in format parsing
5. Reasoning Traps - Logic puzzles embedded in documents
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AdversarialProbe:
    """An adversarial probe designed to expose a specific weakness."""
    probe_id: str
    category: str
    name: str
    description: str
    document: str
    question: str
    correct_answer: str
    trap_answer: str  # The answer a model might give if it falls for the trap
    difficulty: str  # 'easy', 'medium', 'hard'
    target_weakness: str


class StructuralAmbiguityProbes:
    """Probes that test handling of ambiguous document structure."""

    @staticmethod
    def orphaned_content() -> AdversarialProbe:
        """Content that appears between sections without clear ownership."""
        document = """# Project Alpha

## Phase 1: Planning
The initial planning phase establishes core requirements.
Budget: $50,000

Important note: All timelines are tentative.

## Phase 2: Execution
The execution phase implements the plan.
Budget: $150,000

## Phase 3: Review
Final review and assessment.
Budget: $25,000"""

        return AdversarialProbe(
            probe_id="SA_001",
            category="structural_ambiguity",
            name="Orphaned Content",
            description="Tests whether model correctly identifies that 'Important note' belongs to Phase 1 or is document-level",
            document=document,
            question="Which phase does the 'Important note about timelines' belong to?",
            correct_answer="Phase 1 (or arguably document-level/none)",
            trap_answer="Phase 2",
            difficulty="medium",
            target_weakness="Tendency to associate content with following rather than preceding section"
        )

    @staticmethod
    def competing_hierarchies() -> AdversarialProbe:
        """Document with multiple valid structural interpretations."""
        document = """# Report

## Section A
### Subsection A.1
Content for A.1

## Section B
Content for B (no subsections)

### Orphan Subsection
This subsection header appears after Section B's content.
Is it B.1 or a misformatted section?

## Section C
### Subsection C.1
Content for C.1"""

        return AdversarialProbe(
            probe_id="SA_002",
            category="structural_ambiguity",
            name="Competing Hierarchies",
            description="Tests handling of ambiguous subsection placement",
            document=document,
            question="How many subsections does Section B have?",
            correct_answer="Ambiguous - could be 0 or 1",
            trap_answer="1",
            difficulty="hard",
            target_weakness="Assuming well-formed hierarchy when structure is ambiguous"
        )

    @staticmethod
    def depth_confusion() -> AdversarialProbe:
        """Markdown headers that skip levels."""
        document = """# Main Title

### Deep Section (skipped ##)
This section skipped the h2 level.

##### Very Deep (skipped ### and ####)
This skipped multiple levels.

## Normal Section
Back to normal hierarchy.

### Normal Subsection
Properly nested."""

        return AdversarialProbe(
            probe_id="SA_003",
            category="structural_ambiguity",
            name="Depth Confusion",
            description="Tests handling of non-sequential header depths",
            document=document,
            question="What is the depth of 'Deep Section' - is it level 2 (by position) or level 3 (by markdown)?",
            correct_answer="Level 3 by markdown syntax, but structurally ambiguous",
            trap_answer="Level 2",
            difficulty="medium",
            target_weakness="Conflating visual position with explicit depth markers"
        )


class SemanticInterferenceProbes:
    """Probes with similar content designed to cause confusion."""

    @staticmethod
    def similar_entities() -> AdversarialProbe:
        """Multiple entities with similar names."""
        document = """# Employee Directory

## John Smith (Engineering)
- ID: EMP-001
- Department: Engineering
- Location: Building A
- Salary: $95,000

## John Smith (Marketing)
- ID: EMP-047
- Department: Marketing
- Location: Building C
- Salary: $82,000

## Jon Smith (Sales)
- ID: EMP-103
- Department: Sales
- Location: Building B
- Salary: $78,000"""

        return AdversarialProbe(
            probe_id="SI_001",
            category="semantic_interference",
            name="Similar Entities",
            description="Tests disambiguation of similarly-named entities",
            document=document,
            question="What is the salary of John Smith in Marketing?",
            correct_answer="$82,000",
            trap_answer="$95,000 (Engineering John Smith)",
            difficulty="easy",
            target_weakness="Stopping at first match without checking qualifiers"
        )

    @staticmethod
    def updated_values() -> AdversarialProbe:
        """Document with corrections/updates that supersede earlier values."""
        document = """# Quarterly Report

## Q1 Results
Revenue: $1.2M
Expenses: $800K
Profit: $400K

## Q2 Results
Revenue: $1.5M
Expenses: $900K
Profit: $600K

## Corrections
- Q1 Revenue should be $1.3M (accounting error corrected)
- Q1 Profit is therefore $500K

## Summary
Total H1 Revenue: $2.8M
Total H1 Profit: $1.1M"""

        return AdversarialProbe(
            probe_id="SI_002",
            category="semantic_interference",
            name="Updated Values",
            description="Tests whether model uses corrected or original values",
            document=document,
            question="What was the Q1 Revenue?",
            correct_answer="$1.3M (corrected value)",
            trap_answer="$1.2M (original value)",
            difficulty="medium",
            target_weakness="Using first-encountered value instead of tracking updates"
        )

    @staticmethod
    def negation_trap() -> AdversarialProbe:
        """Document with negations that could be missed."""
        document = """# Policy Document

## Access Rules

### Standard Access
- Employees CAN access the main database
- Employees CAN view public reports
- Employees CAN submit expense claims

### Restrictions
- Contractors CANNOT access the main database
- Contractors CANNOT view salary information
- Contractors CAN view public reports

### Exceptions
- Senior contractors with approval CAN access the main database
- No one can view salary information except HR"""

        return AdversarialProbe(
            probe_id="SI_003",
            category="semantic_interference",
            name="Negation Trap",
            description="Tests correct processing of CAN vs CANNOT",
            document=document,
            question="Can contractors access the main database?",
            correct_answer="No (unless senior with approval)",
            trap_answer="Yes",
            difficulty="medium",
            target_weakness="Missing negations when similar positive statements exist"
        )


class PositionalBiasProbes:
    """Probes that exploit known positional biases."""

    @staticmethod
    def primacy_trap() -> AdversarialProbe:
        """Important information buried late in document."""
        document = """# Server Configuration Guide

## Introduction
This guide covers server setup for our standard web application.
Default port: 8080

## Basic Setup
Follow these steps for initial configuration:
1. Install dependencies
2. Configure environment variables
3. Set port to 8080 (standard)

## Network Configuration
Standard network settings apply.
Default port: 8080

## Advanced Configuration
For production deployments, note:
- Enable SSL/TLS
- Configure load balancer
- **IMPORTANT: Production port must be 443, not 8080**

## Troubleshooting
If connection issues occur, verify port 8080 is open."""

        return AdversarialProbe(
            probe_id="PB_001",
            category="positional_bias",
            name="Primacy Trap",
            description="Tests whether late-document corrections override earlier repeated information",
            document=document,
            question="What port should be used for production deployments?",
            correct_answer="443",
            trap_answer="8080",
            difficulty="hard",
            target_weakness="Over-weighting information that appears multiple times early"
        )

    @staticmethod
    def recency_trap() -> AdversarialProbe:
        """Misleading information placed last."""
        document = """# Meeting Notes - Project Delta

## Attendees
Alice (Lead), Bob, Carol, David

## Decisions Made
1. Launch date: March 15th (unanimous)
2. Budget: $500K (approved)
3. Team size: 8 people (confirmed)

## Action Items
- Alice: Finalize specs by Feb 1
- Bob: Prepare infrastructure by Feb 15
- Carol: Complete testing by March 1

## Sidebar Discussion (informal)
David mentioned he personally thinks April might be more realistic,
but this was just his opinion and not a decision."""

        return AdversarialProbe(
            probe_id="PB_002",
            category="positional_bias",
            name="Recency Trap",
            description="Tests whether informal last-mentioned info overrides formal decisions",
            document=document,
            question="What is the launch date for Project Delta?",
            correct_answer="March 15th",
            trap_answer="April",
            difficulty="medium",
            target_weakness="Over-weighting recent/last information regardless of authority"
        )


class FormatBreakingProbes:
    """Probes with edge cases in format parsing."""

    @staticmethod
    def markdown_in_code() -> AdversarialProbe:
        """Markdown formatting inside code blocks."""
        document = """# Documentation

## Usage Example

```python
# Configuration values
config = {
    "# This is NOT a header": "It's a Python comment",
    "value": 42,
    "## Also not a header": "String that looks like markdown"
}
```

## Real Configuration

The actual header (above) describes the real configuration section.
Default value: 100"""

        return AdversarialProbe(
            probe_id="FB_001",
            category="format_breaking",
            name="Markdown in Code",
            description="Tests whether markdown inside code blocks is incorrectly parsed as structure",
            document=document,
            question="How many level-2 headers (##) are in this document?",
            correct_answer="2 (Usage Example and Real Configuration)",
            trap_answer="4 (including the ones in the code block)",
            difficulty="medium",
            target_weakness="Parsing structure inside code blocks"
        )

    @staticmethod
    def nested_quotes() -> AdversarialProbe:
        """Quotes within quotes with attributions."""
        document = """# Interview Transcript

## Question 1

Interviewer: "What did the CEO say about the merger?"

Subject: "She said, 'The merger will close in Q2,' but then later
corrected herself saying 'Actually, Q3 is more likely given regulatory
review times.'"

## Question 2

Interviewer: "And the CFO's view?"

Subject: "He disagreed. His exact words were 'I still believe Q2 is
achievable if we expedite the filings.'"

## Official Statement
The company's official position is that the merger will close in Q3."""

        return AdversarialProbe(
            probe_id="FB_002",
            category="format_breaking",
            name="Nested Quotes",
            description="Tests attribution tracking through nested quotations",
            document=document,
            question="According to the CEO, when will the merger close?",
            correct_answer="Q3 (her corrected statement)",
            trap_answer="Q2 (her initial statement)",
            difficulty="hard",
            target_weakness="Tracking corrections within quoted speech"
        )


class ReasoningTrapProbes:
    """Logic puzzles embedded in documents."""

    @staticmethod
    def conditional_cascade() -> AdversarialProbe:
        """Chained conditionals requiring careful tracking."""
        document = """# Shipping Policy

## Domestic Shipping

- Orders under $25: Standard shipping $5.99
- Orders $25-$50: Standard shipping $3.99
- Orders over $50: FREE standard shipping
- Express shipping: Add $10 to any tier

## International Shipping

- All orders: Base rate $15.99
- Orders over $100: Base rate reduced to $9.99
- Express international: 2x the applicable base rate

## Member Discounts

- Silver members: 10% off shipping costs
- Gold members: 25% off shipping costs
- Platinum members: FREE domestic shipping, 50% off international

## Calculation Rules

Apply member discount AFTER calculating base shipping cost.
Express fees are added BEFORE member discount is applied."""

        return AdversarialProbe(
            probe_id="RT_001",
            category="reasoning_trap",
            name="Conditional Cascade",
            description="Tests multi-step conditional reasoning with order of operations",
            document=document,
            question="What does a Gold member pay for express international shipping on a $120 order?",
            correct_answer="$14.99 (base $9.99 × 2 = $19.98, then 25% off = $14.985)",
            trap_answer="$7.50 (incorrectly applying discount to base then doubling)",
            difficulty="hard",
            target_weakness="Order of operations in multi-step calculations"
        )

    @staticmethod
    def exception_to_exception() -> AdversarialProbe:
        """Rules with exceptions that have their own exceptions."""
        document = """# Access Control Matrix

## General Rule
All employees can access Floor 1 and Floor 2.
No employee can access Floor 3 (Executive).

## Department Exceptions
- Engineering can access Server Room (Floor 2, Room 201)
- Marketing CANNOT access Server Room
- HR can access ALL rooms on Floor 2

## Security Overrides
- No one can access Floor 3 EXCEPT C-level executives
- C-level executives can access all floors
- HOWEVER, even C-level cannot access the Vault (Floor 3, Room 301) without CFO approval

## Time-Based Rules
- After 6 PM, only Security can access Floor 3
- This OVERRIDES all other permissions including C-level"""

        return AdversarialProbe(
            probe_id="RT_002",
            category="reasoning_trap",
            name="Exception to Exception",
            description="Tests handling of nested exceptions and overrides",
            document=document,
            question="Can the CEO access Floor 3 at 8 PM?",
            correct_answer="No (time-based override supersedes C-level exception)",
            trap_answer="Yes (CEO is C-level)",
            difficulty="hard",
            target_weakness="Tracking exception priority and overrides"
        )


def generate_all_probes() -> List[AdversarialProbe]:
    """Generate all adversarial probes."""
    probes = []

    # Structural ambiguity
    probes.append(StructuralAmbiguityProbes.orphaned_content())
    probes.append(StructuralAmbiguityProbes.competing_hierarchies())
    probes.append(StructuralAmbiguityProbes.depth_confusion())

    # Semantic interference
    probes.append(SemanticInterferenceProbes.similar_entities())
    probes.append(SemanticInterferenceProbes.updated_values())
    probes.append(SemanticInterferenceProbes.negation_trap())

    # Positional bias
    probes.append(PositionalBiasProbes.primacy_trap())
    probes.append(PositionalBiasProbes.recency_trap())

    # Format breaking
    probes.append(FormatBreakingProbes.markdown_in_code())
    probes.append(FormatBreakingProbes.nested_quotes())

    # Reasoning traps
    probes.append(ReasoningTrapProbes.conditional_cascade())
    probes.append(ReasoningTrapProbes.exception_to_exception())

    return probes


def create_experiment_protocol() -> Dict:
    """Create the adversarial probe protocol."""
    probes = generate_all_probes()

    return {
        'experiment_name': 'Adversarial Edge Case Probes',
        'version': '1.0',
        'date_created': datetime.now().isoformat(),
        'description': '''
            Adversarial probes designed to expose specific weaknesses in
            LLM document understanding. Each probe targets a known or
            suspected failure mode.
        ''',
        'categories': {
            'structural_ambiguity': 'Documents with unclear or ambiguous hierarchy',
            'semantic_interference': 'Similar content designed to cause confusion',
            'positional_bias': 'Exploiting primacy/recency effects',
            'format_breaking': 'Edge cases in format parsing',
            'reasoning_trap': 'Logic puzzles requiring careful tracking'
        },
        'probes': [
            {
                'probe_id': p.probe_id,
                'category': p.category,
                'name': p.name,
                'description': p.description,
                'difficulty': p.difficulty,
                'target_weakness': p.target_weakness,
                'trap_answer': p.trap_answer
            }
            for p in probes
        ],
        'total_probes': len(probes)
    }


def format_probe_for_testing(probe: AdversarialProbe) -> str:
    """Format a probe for testing."""
    return f"""## Document

{probe.document}

---

## Question

{probe.question}

## Instructions

Read the document carefully and answer the question. Be precise."""


if __name__ == '__main__':
    print("=" * 70)
    print("ADVERSARIAL EDGE CASE PROBES")
    print("=" * 70)

    probes = generate_all_probes()

    print(f"\nGenerated {len(probes)} adversarial probes:\n")

    for probe in probes:
        print(f"[{probe.probe_id}] {probe.name}")
        print(f"  Category: {probe.category}")
        print(f"  Difficulty: {probe.difficulty}")
        print(f"  Target: {probe.target_weakness}")
        print(f"  Trap: {probe.trap_answer}")
        print()

    # Save protocol
    protocol = create_experiment_protocol()
    protocol_path = Path(__file__).parent.parent.parent / 'data' / 'stimuli'
    protocol_path.mkdir(parents=True, exist_ok=True)

    with open(protocol_path / 'adversarial_probes_protocol.json', 'w') as f:
        json.dump(protocol, f, indent=2)

    print(f"Protocol saved to: {protocol_path / 'adversarial_probes_protocol.json'}")
