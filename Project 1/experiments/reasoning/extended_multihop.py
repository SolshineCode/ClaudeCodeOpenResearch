"""
Extended Multi-Hop Generator

Wraps `MultiHopDocumentGenerator` to support 6+ hops. The shipped generator
caps hops at `len(self.domain['entities'])` (default 5) because line 109
uses `random.sample` which can't draw with replacement. This module
relaxes that cap by drawing entity types **with replacement** when the
requested hop count exceeds the pool size, distinguishing instances by
index (e.g. "Department A", "Department B", ..., "Department F" for an
8-hop chain on the 5-entity 'organization' domain).

Usage:
    from extended_multihop import ExtendedMultiHopGenerator
    g = ExtendedMultiHopGenerator(seed=42, domain='organization')
    doc, chain = g.generate_reasoning_chain(num_hops=8, chain_type='implicit')

The output shape is identical to MultiHopDocumentGenerator's, so all
downstream code (live_api_runner, harder_variants, render_markdown) keeps
working unchanged.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional

# Ensure we can import the original module regardless of sys.path state
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from multi_hop_document import MultiHopDocumentGenerator, ReasoningChain  # noqa: E402


class ExtendedMultiHopGenerator(MultiHopDocumentGenerator):
    """Multi-hop generator that supports num_hops > len(domain['entities'])."""

    def generate_reasoning_chain(self, num_hops: int, chain_type: str = 'explicit'):
        # Same logic as parent up to entity_types selection — duplicated
        # because the base class doesn't expose a hook point. The change is
        # one line: random.sample (no replacement) -> a fill-then-pad
        # strategy that wraps the entity pool when num_hops + 1 exceeds it.
        pool = list(self.domain['entities'])
        needed = num_hops + 1
        if needed <= len(pool):
            entity_types = random.sample(pool, needed)
        else:
            # Take all unique types in random order, then pad by repeating
            # the (re-shuffled) pool until we have enough.
            entity_types = random.sample(pool, len(pool))
            while len(entity_types) < needed:
                more = random.sample(pool, min(len(pool), needed - len(entity_types)))
                entity_types.extend(more)

        entities = []
        for i, etype in enumerate(entity_types):
            entity = {
                'id': self._generate_entity_id(etype, i),
                # 'name' must stay unique across the chain since the prompt
                # uses entity name to disambiguate; A, B, ..., Z then AA, AB.
                'name': f"{etype} {self._index_letter(i)}",
                'type': etype,
                'section_num': f"{i + 1}",
                'properties': {}
            }
            props = random.sample(self.domain['properties'],
                                   k=min(3, len(self.domain['properties'])))
            for prop in props:
                entity['properties'][prop] = self._generate_property_value(prop)
            entities.append(entity)

        # Build chain (verbatim from parent)
        hops = []
        for i in range(num_hops):
            current = entities[i]
            next_entity = entities[i + 1] if i + 1 < len(entities) else None

            if chain_type == 'explicit':
                link = f"(See Section {next_entity['section_num']})" if next_entity else None
            elif chain_type == 'implicit':
                link = f"managed by the {next_entity['type'].lower()}" if next_entity else None
            else:
                if i % 2 == 0:
                    link = f"(Refer to {next_entity['name']})" if next_entity else None
                else:
                    link = f"overseen by {next_entity['name']}" if next_entity else None

            if next_entity:
                relation = random.choice(self.domain['relations'])
                fact = f"{current['name']} {relation.replace('_', ' ')} {next_entity['name']}"
            else:
                target_prop = random.choice(list(current['properties'].keys()))
                fact = (f"The {target_prop.replace('_', ' ')} is "
                        f"{current['properties'][target_prop]}")

            hops.append({
                'location': f"Section {current['section_num']}",
                'entity': current['name'],
                'fact': fact,
                'link_to_next': link,
            })

        final_entity = entities[-1]
        target_prop = random.choice(list(final_entity['properties'].keys()))
        answer = final_entity['properties'][target_prop]

        first_entity = entities[0]
        question = (f"Starting from {first_entity['name']}, follow the chain of "
                    f"relationships to find the {target_prop.replace('_', ' ')} of "
                    f"the final entity in the chain.")

        chain = ReasoningChain(
            hops=hops, question=question, answer=answer, chain_type=chain_type,
        )
        document = self._build_document(entities, chain)
        return document, chain

    @staticmethod
    def _index_letter(i: int) -> str:
        """0 -> A, 1 -> B, ..., 25 -> Z, 26 -> AA, 27 -> AB, ..."""
        if i < 26:
            return chr(65 + i)
        first = chr(65 + (i // 26) - 1)
        second = chr(65 + (i % 26))
        return first + second
