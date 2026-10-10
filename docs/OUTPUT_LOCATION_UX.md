# UX Decision — Audio Output Location

## Problem

The upstream application required the user to choose an output folder before converting any file. For the common use case (extracting audio from a recording beside its video), that is unnecessary work. It also hid the exact destination until the person made a selection.

## Decision

**Automatic by default, optional override, always visible.**

| Context | Default destination | UI and optional action |
| --- | --- | --- |
| No videos selected | Destination determined by each future video | Explain that output defaults to each source video's folder |
| One video | Parent folder of that video | Display its full folder path |
| Several videos in one folder | That shared parent folder | Display the full shared path |
| Several videos from different folders | Each video's own parent folder | Display the first three paths and total count; reveal all paths in a tooltip and display each video's exact destination in its list tooltip. Suggest an optional shared folder in place, without a modal |
| Custom folder selected | All outputs go into that folder | Display the full selected path and offer **Use source folders** |
| Folder picker cancelled | Destination stays unchanged | Do not interrupt conversion |
| Video list cleared | Automatic per-source behavior restored | Avoid accidentally sending a new batch to an old custom folder |

The **Convert** action must never require a manually selected destination. A selected destination that no longer exists is reported as an error. Source folders that have disappeared or become unwritable fail individually with a clear message, allowing the batch to continue. Existing outputs are not intentionally overwritten and filename conflicts use numbered suffixes.

The same policy applies to MP3, WAV and AAC outputs.

## Why a non-modal suggestion?

Videos from distinct folders introduce a meaningful choice: save alongside each original or collect everything into one folder. The user should **see the available choice** but not be forced to respond to a routine dialog. The application uses an inline contextual message and an explicitly optional button.

This follows these NN/g principles:

1. **Visibility of system status:** display the active save destination before conversion. https://www.nngroup.com/articles/visibility-system-status/
2. **User control and freedom:** let users choose a common folder and return to defaults in one action. https://www.nngroup.com/articles/user-control-and-freedom/
3. **Recognition rather than recall:** expose destinations in the interface and file tooltips rather than forcing users to remember file paths. https://www.nngroup.com/articles/recognition-and-recall/
4. **Error prevention:** prefer a good default and protect existing output. https://www.nngroup.com/articles/ten-usability-heuristics/
5. **Avoid needless confirmations:** NN/g advises against confirmation dialogs for routine actions. https://www.nngroup.com/articles/confirmation-dialog/

These articles establish general UX heuristics, not a tested NN/g endorsement of this specific conversion flow. Validate with actual usage and revise if needed.

## Acceptance criteria

- [ ] A video in one folder can be converted without selecting an output destination.
- [ ] Two videos from the same directory default to that directory.
- [ ] Two videos from different directories save alongside their originals without prompting in a modal.
- [ ] An inline prompt offers a common folder when multiple original directories are present.
- [ ] The save location remains visible before conversion; tooltips reveal full paths.
- [ ] A chosen common folder applies to every input and **Use source folders** restores default behavior.
- [ ] Cancelling the folder picker does not block conversion or change the current destination.
- [ ] Clearing the selection resets any custom destination.
- [ ] Identical basenames in separate folders remain unchanged when using per-source destinations; duplicates in one common destination receive suffixes.
- [ ] Conversion progress, cancellation and existing file protections still work.

The automated tests cover the primary routing and UI-state scenarios. A manual Windows shortcut (pythonw.exe) conversion test is still required before merging.
