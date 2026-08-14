# tech-wiki-skills

Claude Code용 개인 스킬 모음. tech-wiki-vault 스타일 vault(`raw/` → `Cards/` → `Blog-drafts/`)를 자산화하는 파이프라인을 구성한다.

## 구성

| 스킬 | 역할 |
|---|---|
| `tech-research-card` | 0단계(원문 저장+태깅) + 1~2단계(깊이 게이트 분류 → 카드 생성) |
| `tech-research-card-blog` | 3단계: 카드 → 블로그 초안 승격 |
| `tech-wiki-factcheck` | 4단계: 블로그 초안의 문헌조사 수치·벤치마크 재검증 |
| `tech-wiki-audit` | vault 디렉토리 구조가 `CLAUDE.md` 규칙에서 벗어났는지 감사 |
| `tech-wiki-pipeline` | 위 4개 + `humanize-korean`(별도 플러그인)을 순서대로 위임하는 오케스트레이터. 원문단계 팩트체크(신규 로직)도 여기 있음 |

각 스킬 폴더의 `SKILL.md`가 실제 지침이다. `tech-wiki-pipeline`은 얇은 래퍼라서 나머지 로직을 복붙하지 않는다 — 각 하위 스킬을 고치면 파이프라인 전체에 자동 반영된다.

## 별도 설치가 필요한 의존성

`tech-wiki-pipeline`의 5단계(휴머나이즈)는 이 저장소에 없는 **`humanize-korean` 플러그인**을 호출한다. 이 저장소만 클론해서는 그 단계가 동작하지 않으니, 새 컴퓨터에서는 Claude Code 마켓플레이스에서 `humanize-korean` 플러그인을 별도로 설치해야 한다.

또한 `tech-wiki-pipeline`의 5단계는 Python(`prepare_monolith_input.py`, `verify_gates.py`)이 있으면 정량 채점·결정적 게이트를 쓴다. Python이 없는 환경에서는 자동으로 수동 경로(진단→겨냥 윤문 2콜, 사람이 직접 대조 검토)로 넘어가도록 스킬 안에 이미 안내가 있다.

## 새 컴퓨터에서 쓰는 법

```bash
git clone <이 저장소 URL> ~/claude-skills
```

그 다음 `~/.claude/skills/` 아래에 각 스킬을 가리키는 **NTFS 접합점(junction)**을 만든다(심볼릭 링크는 관리자 권한/개발자 모드가 필요해서 번거로울 수 있어 junction을 쓴다). PowerShell에서:

```powershell
$skills = @('tech-research-card','tech-research-card-blog','tech-wiki-factcheck','tech-wiki-audit','tech-wiki-pipeline')
foreach ($name in $skills) {
    New-Item -ItemType Junction -Path "$HOME\.claude\skills\$name" -Target "$HOME\claude-skills\$name"
}
```

macOS/Linux라면 junction 대신 `ln -s`(심볼릭 링크)를 쓴다:

```bash
for name in tech-research-card tech-research-card-blog tech-wiki-factcheck tech-wiki-audit tech-wiki-pipeline; do
  ln -s "$HOME/claude-skills/$name" "$HOME/.claude/skills/$name"
done
```

이렇게 하면 `~/.claude/skills/`의 실제 파일이 이 저장소 안에 있는 상태로 유지되어, 앞으로 스킬을 수정하면 바로 git으로 커밋·푸시할 수 있다.

## 수정할 때 주의

- vault의 `CLAUDE.md`가 최종 규칙이다. 스킬은 그 규칙을 실행하는 도구일 뿐이니, 규칙이 바뀌면 vault의 `CLAUDE.md`를 먼저 고치고 스킬을 맞춘다.
- `tech-wiki-pipeline`에 개별 스킬 로직을 복붙하지 않는다(얇은 래퍼 원칙).
