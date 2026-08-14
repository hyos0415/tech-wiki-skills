---
name: tech-wiki-audit
description: tech-wiki-vault의 디렉토리 구조가 CLAUDE.md 규칙에서 벗어났는지 점검하고 정리한다. 사용자가 "vault 정리해줘", "구조 점검해줘", "규칙에서 벗어난 거 있는지 봐줘"라고 요청하거나, WORKFLOW.md/README.md/번호코드 파일명 같은 낯선 것들이 보인다고 말할 때 사용. tech-research-card 계열 스킬이 카드를 만들 때가 아니라, 이미 쌓인 vault 전체를 사후 점검할 때 쓰는 별도 도구다.
allowed-tools: Read Write Bash Glob
---

# Vault 구조 감사

vault의 `CLAUDE.md`에 정의된 규칙(최상위 문서 3개, 폴더 5개, flat 구조, 파일명=제목, frontmatter에 링크 금지)에서 벗어난 부분을 찾아 정리한다. vault 루트에서 실행한다.

## 점검 순서 (전부 bash로 기계적 검사 — 판단이 필요한 항목만 표시하고 나머지는 자동 수정)

### A. 최상위 파일 확인

```bash
find . -maxdepth 1 -name "*.md" | sed 's|^\./||'
```
`CLAUDE.md`, `index.md`, `log.md` 외의 것이 나오면 위반. 해당 파일을 읽어서 살릴 내용이 있으면(예: 유용한 워크플로우 설명) `CLAUDE.md`나 `index.md`에 요약해서 병합할지 사용자에게 묻고, 병합 여부와 무관하게 원래 파일은 삭제 대상으로 보고한다. **삭제는 사용자 확인 후 실행.**

### B. 최상위 폴더 확인

```bash
find . -maxdepth 1 -type d -not -path "./.git*" -not -path "./.obsidian*" -not -path "." | sed 's|^\./||'
```
`raw`, `Scratch`, `Cards`, `Blog-drafts`, `Templates` 외의 것(예: `Humanize/`)이 나오면 위반. 폴더 안 파일을 확인해서 어느 정식 폴더로 옮길지(대부분 `Cards/`나 `Blog-drafts/`) 판단해 사용자에게 제안하고, 승인 후 이동·원래 폴더 삭제.

### C. Flat 구조 확인 (하위 폴더 금지)

```bash
find raw Cards Blog-drafts -mindepth 1 -maxdepth 1 -type d 2>/dev/null
```
뭔가 나오면 그 폴더 안의 `.md` 파일들을 상위 폴더로 끌어올린다. **이건 기계적 이동이라 자동으로 실행**하되, 실행 후 반드시 D·F 점검을 다시 돈다(파일명이 번호 코드였을 수 있고, 이동으로 상대링크가 깨질 수 있음).

### D. 번호 코드 파일명 확인

```bash
find raw Cards Blog-drafts -maxdepth 1 -regex '.*/[0-9]+_.*\.md' 2>/dev/null
```
나오면, 해당 파일을 열어 `##` 제목이나 내용에서 적절한 제목을 뽑아 그 제목으로 리네임할지 제안한다. **리네임은 링크를 깨뜨릴 수 있으므로 사용자 승인 후 실행하고, 실행 후 F를 다시 돈다.**

### E. Frontmatter 링크 오염 확인 (자동 수정)

```bash
for f in raw/*.md Cards/*.md Blog-drafts/*.md; do
  [ -f "$f" ] || continue
  awk '/^---$/{c++; next} c==1' "$f" | grep -n '\[\[' && echo "  ↑ $f"
done
```
frontmatter(첫 `---`와 두번째 `---` 사이) 안에 `[[`가 있으면 위반. **이건 규칙이 명확하니 자동으로 고친다**: 그 줄을 frontmatter에서 빼고, 본문 상단에 `- 원문: [[제목]]` 또는 `- 관련 문서: [[제목]]` 형식의 텍스트 줄로 옮긴다. 필드명에 따라 적절히 매핑(source/original_source → 원문, related/derived_from_cards → 관련 문서).

### F. 깨진 링크 확인

```bash
comm -23 \
  <(grep -rho '\[\[[^]]*\]\]' raw Cards Blog-drafts index.md 2>/dev/null | sed 's/\[\[//; s/\]\]//; s/|.*//' | sort -u) \
  <(find raw Cards Blog-drafts -name "*.md" | sed 's/.*\///; s/\.md$//' | sort -u)
```
나오면 실제 파일명과 대조해서 오타·공백 차이를 찾는다. 가까운 후보가 명확하면 고치자고 제안하고, 애매하면 사용자에게 "이 링크, 어떤 파일을 가리키려던 거야?"라고 묻는다. 대상 파일이 아예 없으면(빈 파일이 생성된 경우) 그 빈 파일을 지워도 되는지 확인 후 삭제하고, 원래 링크는 대상이 생기기 전까지 일반 텍스트로 되돌린다.

### G. 고아 노드 확인 (Templates 제외, 보고만 함)

```bash
for f in raw/*.md Cards/*.md Blog-drafts/*.md; do
  [ -f "$f" ] || continue
  title=$(basename "$f" .md)
  has_out=$(grep -c '\[\[' "$f" 2>/dev/null)
  has_in=$(grep -rl "\[\[$title\]\]" raw Cards Blog-drafts index.md 2>/dev/null | grep -v "^$f$" | wc -l)
  [ "$has_out" -eq 0 ] && [ "$has_in" -eq 0 ] && echo "고아: $f"
done
```
나오면 그냥 보고만 한다 — 고아라는 게 항상 잘못은 아니고(막 만든 첫 카드일 수 있음), 삭제나 수정을 자동으로 하지 않는다.

## 보고 형식

각 항목(A~G)을 표로 정리해서 보여준다: 위반 여부, 발견된 파일, 제안하는 조치, 자동/승인필요 여부. 자동 수정 항목(C, E)은 먼저 실행 결과를 보여주고, 승인 필요 항목(A, B, D, F)은 조치 전에 사용자 확인을 받는다.

## 실행 후

모든 조치가 끝나면 F(깨진 링크 확인)를 마지막에 한 번 더 돌려서, 정리 작업 자체가 새로운 깨진 링크를 만들지 않았는지 확인한다. 확인되면 `log.md`에 한 줄 기록한다: `| 날짜 | vault 구조 감사 | 발견·수정한 위반 요약 | - |`
