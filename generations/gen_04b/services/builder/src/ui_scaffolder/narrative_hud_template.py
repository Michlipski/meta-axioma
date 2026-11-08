"""Narrative HUD Vanilla JS & Plain-English Translation Engine (`narrative_hud_template.py`).

Enforces:
- Waterloo SYDE 361 Human Ergonomics (P_1): Non-technical users must never be forced to decipher raw JSON.
- Plain-English Narrative Translation: Translates state diffs (ΔS = S_{t+1} - S_t) into human-centered explanations.
- Zero-CDN compliance ([HERM-005]): 100% self-contained vanilla JavaScript.
- Injection Defense: Safe textContent DOM assignment preventing script injection vulnerabilities.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def format_narrative_diff(
    diff: Dict[str, Any] | str,
    action_name: str = "",
    context: str = "",
) -> str:
    """Translates state diffs into concise plain-English explanations for User Zero.
    
    Addresses Waterloo SYDE 361 Human Ergonomics.
    """
    if isinstance(diff, str):
        return diff.strip()

    if not diff:
        return f"{action_name}: System state steady. Invariant equilibrium maintained." if action_name else "System state steady. No mutations observed."

    parts = []
    if action_name:
        parts.append(f"Executed {action_name}.")

    # Check for additions / created nodes
    if "added" in diff or "created" in diff:
        items = diff.get("added") or diff.get("created")
        if isinstance(items, list):
            parts.append(f"Added {len(items)} entity/node{'s' if len(items) != 1 else ''} ({', '.join(str(i) for i in items[:3])}).")
        elif isinstance(items, (str, dict)):
            parts.append(f"Added entity: {items}.")

    # Check for modifications / property mutations
    if "modified" in diff or "updated" in diff:
        mod = diff.get("modified") or diff.get("updated")
        if isinstance(mod, dict):
            field_updates = [f"{k} -> {v}" for k, v in mod.items()]
            parts.append(f"Updated properties: {', '.join(field_updates[:3])}.")
        elif isinstance(mod, list):
            parts.append(f"Modified {len(mod)} element{'s' if len(mod) != 1 else ''}.")

    # Check for removals / deletions
    if "removed" in diff or "deleted" in diff:
        del_items = diff.get("removed") or diff.get("deleted")
        if isinstance(del_items, list):
            parts.append(f"Removed {len(del_items)} entity/node{'s' if len(del_items) != 1 else ''}.")
        else:
            parts.append(f"Removed entity: {del_items}.")

    # Fallback to general diff key summary
    if not parts or (len(parts) == 1 and action_name):
        keys = list(diff.keys())
        parts.append(f"Observed changes across {len(keys)} domain attribute{'s' if len(keys) != 1 else ''} ({', '.join(keys[:3])}).")

    if context:
        parts.append(f"Ecosystem impact: {context}.")

    return " ".join(parts)


class NarrativeHUDTemplate:
    """Renders canonical vanilla JS plain-English ecosystem narrative HUD controller."""

    @staticmethod
    def render_js() -> str:
        """Emits the full NarrativeHUDController vanilla JS implementation."""
        return '''// =========================================================================
// NarrativeHUDController: User Zero Plain-English Ecosystem Translator
// Enforces Waterloo SYDE 361 (Human Ergonomics P_1) & Zero-CDN [HERM-005]
// =========================================================================

class NarrativeHUDController {
  constructor(hudElement, options = {}) {
    this.hudElement = typeof hudElement === 'string' ? document.querySelector(hudElement) : hudElement;
    this.options = Object.assign({
      contextTitle: 'Ecosystem Narrative',
      maxHistory: 15,
      defaultMessage: 'Ready. Workspace initialized in baseline invariant equilibrium.'
    }, options);

    this.history = [];
    this.init();
  }

  init() {
    if (this.hudElement) {
      this.update(this.options.defaultMessage);
    }
  }

  // Translates state diffs ΔS = S_{t+1} - S_t into concise, 2-sentence plain English
  translateDiff(diff, actionName = '') {
    if (typeof diff === 'string') {
      return diff;
    }

    if (!diff || Object.keys(diff).length === 0) {
      return actionName 
        ? `Executed action: "${actionName}". System state remains in verified equilibrium.`
        : 'System state steady. No entity mutations observed.';
    }

    const sentences = [];
    if (actionName) {
      sentences.push(`Triggered ${actionName}.`);
    }

    // Deconstruct additions
    if (diff.added || diff.created) {
      const items = diff.added || diff.created;
      if (Array.isArray(items)) {
        sentences.push(`Added ${items.length} entity: ${items.slice(0, 3).map(i => i.name || i.id || i).join(', ')}.`);
      } else {
        sentences.push(`Created entity: ${items.name || items.id || JSON.stringify(items)}.`);
      }
    }

    // Deconstruct modifications
    if (diff.modified || diff.updated) {
      const mods = diff.modified || diff.updated;
      if (typeof mods === 'object') {
        const changes = Object.keys(mods).map(k => `${k} to ${mods[k]}`);
        sentences.push(`Updated ${changes.slice(0, 2).join(', ')}.`);
      }
    }

    // Deconstruct deletions
    if (diff.removed || diff.deleted) {
      const dels = diff.removed || diff.deleted;
      sentences.push(`Removed ${Array.isArray(dels) ? dels.length : 1} item.`);
    }

    // Handle domain-specific narrative override
    if (diff.narrative) {
      return diff.narrative;
    }

    if (sentences.length === 0) {
      const changedKeys = Object.keys(diff).join(', ');
      sentences.push(`System state transitioned across attributes: ${changedKeys}.`);
    }

    return sentences.slice(0, 2).join(' ');
  }

  // Safe DOM textContent assignment preventing XSS / script injection
  update(narrativeText) {
    if (!this.hudElement) return;

    const timestamp = new Date().toLocaleTimeString();
    this.history.unshift({ timestamp, narrative: narrativeText });
    if (this.history.length > this.options.maxHistory) {
      this.history.pop();
    }

    // Update active narrative element safely
    const textNode = this.hudElement.querySelector('.narrative-text') || this.hudElement;
    textNode.textContent = narrativeText;

    // Optional badge or timestamp update
    const timeNode = this.hudElement.querySelector('.narrative-timestamp');
    if (timeNode) {
      timeNode.textContent = timestamp;
    }
  }

  ingestStateDiff(diff, actionName = '') {
    const text = this.translateDiff(diff, actionName);
    this.update(text);
    return text;
  }
}
'''
