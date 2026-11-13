---
name: python-version
description: "Read this file before you change `requires-python`, the Python versions of the CI matrix, or the minimum Home Assistant version of hass-gaggiuino."
metadata:
  type: feedback
---

- `requires-python` of `pyproject.toml` is the same as the `requires-python` of the newest release of Home Assistant Core. The CI matrix runs only the Python versions that this range permits.
- To read the current value, run these two commands. The first gives the tag of the newest release, and the second gives the line of that tag:

```bash
gh api repos/home-assistant/core/releases/latest --jq .tag_name
gh api -H "Accept: application/vnd.github.raw" "repos/home-assistant/core/contents/pyproject.toml?ref=<tag>" | grep -m1 requires-python
```

- Before a change of the library, make sure that `requires-python` agrees with that value. If it does not agree, change `requires-python`, the CI matrix and the classifiers first, in their own commit.
- On Python 3.14 and later, do not use `from __future__ import annotations`. Remove it from each file that a change touches.
- A raise of the minimum Python also raises the minimum Home Assistant of hass-gaggiuino in its `hacs.json`, because an older Home Assistant cannot install the library. The minimum is the first release of Home Assistant Core with the same `requires-python`. Find it with the second command and older tags, for example `2026.3.0` for `>=3.14.2`.
