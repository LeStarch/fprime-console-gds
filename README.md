# F´ Console GDS

A terminal (console) ground data system for [F´](https://fprime.jpl.nasa.gov): the latest value of every telemetry
channel on the left, events colourized by severity in the main area, and commanding along the bottom. It is built on
the [F´ GDS](https://github.com/nasa/fprime-gds) (dictionaries, the standard pipeline, command encoding and its
`data_transport` plugins) and on [Textual](https://textual.textualize.io/).

## Install

```
pip install "fprime-gds @ git+https://github.com/nasa/fprime-gds@devel"   # until a release after 4.4.1
pip install git+https://github.com/LeStarch/fprime-console-gds
```

The `data_transport` plugin category this tool connects through was added to the F´ GDS after release 4.4.1, hence
the first line. The default transport, `yamcs`, is provided by the separate
[fprime-yamcs](https://github.com/fprime-community/fprime-yamcs) package and must be installed to be used; any
other installed transport is chosen with `--data-transport-selection`.

## Run

```
fprime-console-gds --dictionary <dictionary.json>                                    # yamcs at http://localhost:8090
fprime-console-gds --dictionary <dictionary.json> --data-transport-selection zmq     # a running fprime-gds
```

`fprime-tui` is the same command under a shorter name. The transport and dictionary arguments are those of the F´
GDS command line tools; `--max-events` bounds the events kept (default 5000).

## Use

- **Telemetry and events** are filtered as in the GDS tables: case-insensitive words that must all appear in the
  row, with `-or-` between two words to accept either. Events also have one toggle per severity. `Enter` on a row
  shows it in full.
- **Commanding** offers a command drop-down with one field per argument and a command string
  (`component.MNEMONIC, arg1, "string, with comma"`) that can be typed or pasted; the two stay in step. Arguments
  are checked with the dictionary types before anything is sent. Commands go out one at a time in the order
  entered, and are kept in a history that reloads a command when selected. Command names may be typed in any
  case, part of a name lists the matching commands, and array/serializable arguments are JSON with the bare words
  of the GDS accepted (`[ONE, TWO]`, `{first: ONE}`).
- **Send safety:** a send key pressed straight after another control key (within a quarter of a second), or while
  the form and the command string name different commands, sends nothing and says so: keys typed ahead of the
  screen must not send what is not shown. When a send fails, the commands waiting behind it are dropped.
- **Keys:** `F2`/`F3`/`F4` focus Commands/Telemetry/Events and `F6`/`Shift+F6` cycle them (`Ctrl+Tab` does too in
  terminals that pass it on; most do not), `Tab` moves between fields, `/` focuses the panel's filter, `Esc` leaves
  a field, `Enter` sends a command or shows the selected row, `F5` sends from any commanding field, `Ctrl+L` clears
  the event list, `F1` shows help, `Ctrl+Q` quits.
- **Small terminals:** columns are fitted to the panel, cutting long names on the left and long values on the
  right. Below 100 columns telemetry and events share the upper area, one at a time (`F3`/`F4`); FATAL and
  WARNING_HI events that arrive while telemetry is shown are announced in the status line.

## Colours

Severity and limit colours are chosen to be told apart with normal, protan, deutan and tritan colour vision
(Okabe-Ito hues), and to meet the WCAG AA contrast ratio against the dark background; `tests/test_colours.py`
checks every pair under simulation. Colour is never the only cue: the severity is a text column, FATAL is a filled
row, WARNING_HI is bold, and telemetry outside its limits is marked `!R`, `!O` or `!Y`. The colours are exact in
terminals with 24-bit colour and approximated elsewhere.

## Untrusted text

Text received from the deployment is displayed literally: terminal control characters are replaced, it is never
interpreted as markup, and each field is capped in length.

## Develop

```
pip install -e ".[test]"
pytest
```
