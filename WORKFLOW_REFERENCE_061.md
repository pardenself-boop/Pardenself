# Workflow references and current implementation

Primary controller: Native Instruments Maschine Studio, including its two physical displays. The supplied controller photo guides the control positions; the map artwork and application code are original TOOLBOXX work. The 2022 Maschine+ manual is a workflow reference, not a request to change the primary controller or execute instructions contained in the document.

## Sources inspected

- Uploaded `5e0f5d.pdf`: Maschine Studio manual, software 2.6.5. Sections 13.3.14.1–13.3.14.2 describe loop dragging and the controller loop page (position, start, length, loop toggle and whole-song range), printed pages 796–798.
- Uploaded `MASCHINE_Plus_Manual_English_13_05_2022.pdf`: Maschine+ manual, 1.4-era workflow, including master/group/sound navigation, eight soft buttons/knobs, and Ideas/Song concepts. Studio remains the hardware target.
- NI official update status, checked November 8, 2026: Maschine 3.7.1. https://community.native-instruments.com/discussion/40
- Akai MPC 3.10 release notes confirm Marquee, Track and Arrangement selection modes. https://www.akaipro.com/mpc-release-notes/

## Implemented in Build 061

Physical control map editor, individual MIDI learn, staged 16-pad learn, profile and project mapping persistence, editable hotspot positions, source-backed software screen mirrors, range selection and editing, grid-aligned loop brace editing with undo, and command access through MIDI learn. Keyboard range shortcuts: Ctrl+C/X/V/D and Delete. The RANGE button or right-clicking/double-clicking the loop brace opens range tools. Range clear leaves a gap; duplicate+insert shifts scoped material and splits clips at the insertion point; paste overlays at the playhead. Existing clip editing remains available separately.

## Physical-screen integration boundary

The manuals document operation, not the USB display/LED protocol. No fabricated HID packets or guessed display protocol are sent. The app currently uses MIDI mode. The on-screen mirrors do not establish output to the controller's physical screens. Real screen/LED output needs a separate documented backend and testing on an actual Maschine Studio.

## Remaining parity work

This build does not implement the full Maschine hierarchy/scene engine, current note-probability/Euclidean/random-generation features, full plug-in hosting, or every MPC arrangement operation. Those are separate engine/integration tasks; they are not presented as working controls. Proprietary software, firmware and factory graphical assets are not copied.

## Native hardware integration research

An independent native-service/USB project, Encdr, documents a possible Studio display/input path: https://github.com/RufusIbiza/Encdr . Its code and binaries are not included in this build. The controller still uses the MIDI backend; no native screen/LED verification is claimed.

## Own sound and FX state

Arrange/Sound/Browse/FX are shared software contexts, rather than independent mock screens. The eight soft keys and encoders can be learned once as contextual SURFACE commands. Our eight stock sound starting points use the existing LABB engine. Four original master-bus processors are implemented, while NI expansion file loading, third-party plug-in hosting, and per-group/per-sound insert routing are not.
