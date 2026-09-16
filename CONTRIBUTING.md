# Contributing

## What Belongs Here

Directory entries should:

- Have publicly available source code under a recognized open-source license. Paid binaries or hosted features are fine.
- Provide a usable voice typing or dictation workflow through an app, keyboard, menu bar utility, or CLI, with output to an app, text field, clipboard, or terminal.
- Have a public repository and a working release or install path. Archived projects qualify only if they remain usable.
- Show evidence of real users. As rough guidelines, look for **~50+ GitHub stars** (or other evidence such as distro packaging, independent write-ups, or non-author issue activity) and **~3+ months** since the first public commit. These are flexible guidelines, not hard cutoffs; meeting the numbers alone is not enough.

Meeting bots, note takers, and general transcription tools without voice typing workflows are outside the directory's scope.

## Adding an Entry

Add a row to the [README directory](README.md#directory) in **case-insensitive alphabetical order**:

```markdown
| [Name](https://github.com/user/repo)<br/><br/>![stars](https://img.shields.io/github/stars/user/repo?style=plastic&label=%E2%98%85) | Platforms | Mode | Engine | Summary |
```

Replace `user/repo` in both URLs with the project's GitHub owner and repository name.

| Column | Guidelines |
| --- | --- |
| Name | Use the project's name and link to its source repository. Include the star badge as shown above. |
| Platforms | List all supported platforms, comma-separated, including `Web` if supported. |
| Mode | Use `Local` for on-device recognition or `Hybrid` for tools supporting both local and cloud recognition. |
| Engine | Name the speech-to-text engines used, e.g. `Whisper.cpp, Faster Whisper`. |
| Summary | Write one factual sentence in sentence case, ending with a period. Focus on distinguishing features and relevant caveats; avoid marketing language. |

Open a pull request titled `Add [Project Name]`. Self-submissions are welcome; disclose if you are the author or a maintainer. The same criteria apply to all submissions.

### Optional Badge

Once your project is listed, you’re welcome to add this badge to your README to highlight its inclusion in Awesome Voice Typing:

```markdown
[![Listed in Awesome Voice Typing](https://img.shields.io/badge/Listed_in-Awesome_Voice_Typing-436D99?style=for-the-badge&labelColor=24292F)](https://github.com/primaprashant/awesome-voice-typing)
```

## Updating or Removing an Entry

For updates, edit the relevant row and link to supporting release notes, commits, or documentation in your PR description when possible.

For projects that no longer meet the criteria above, open an issue or PR explaining why the entry should be removed.
