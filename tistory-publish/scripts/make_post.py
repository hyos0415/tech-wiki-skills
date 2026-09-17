#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Blog-drafts/*.md -> 티스토리 발행용 사본 + 핸드오프 매니페스트.

사용법:
    python make_post.py "<draft.md>" "<out_dir>" [--slug SLUG]

산출물:
    <out_dir>/<slug>-발행용.md    붙여넣을 본문
    <out_dir>/<slug>-발행.json    제목 + 검증 수치 + 링크 목록

구조가 깨지면(헤딩·표·링크 개수가 변하면) 파일을 쓰지 않고 실패한다.
"""
import io
import json
import os
import re
import sys
from datetime import datetime

# ---------- 구조 판별 ----------
# 소프트 줄바꿈을 합칠 때 건드리면 안 되는 줄.
_STRUCT = (
    re.compile(r'^```'),          # 코드펜스
    re.compile(r'^\|'),           # 표
    re.compile(r'^>'),            # 인용
    re.compile(r'^#{1,6}\s'),     # 헤딩
    re.compile(r'^[-*+]\s'),      # 불릿
    re.compile(r'^\d+\.\s'),      # 번호 리스트
    re.compile(r'^-{3,}$'),       # 수평선
)
# 이 줄들 "뒤"에는 다음 줄을 이어붙이지 않는다.
_NO_JOIN_AFTER = re.compile(r'^(```|\||-{3,}$|#{1,6}\s)')


def is_struct(line):
    s = line.strip()
    if not s:
        return True
    return any(p.match(s) for p in _STRUCT)


def count(text):
    """구조 지문. 변환 전후로 같아야 한다 (h1 제외 — 의도적으로 제거하므로)."""
    lines = text.split('\n')
    return {
        'h2': sum(1 for l in lines if re.match(r'^## ', l)),
        'h3': sum(1 for l in lines if re.match(r'^### ', l)),
        'table_pipes': sum(1 for l in lines if l.startswith('|')),
        'quotes': sum(1 for l in lines if l.startswith('>')),
        'lists': sum(1 for l in lines if re.match(r'^\s*[-*+] ', l)),
        'links': len(re.findall(r'\]\(https?://', text)),
        'code_fences': sum(1 for l in lines if l.strip().startswith('```')),
        'backticks': text.count('`'),
    }


def unwrap(text):
    """문단 안의 소프트 줄바꿈을 공백으로 합친다.

    티스토리는 소프트 줄바꿈을 <br> 강제 개행으로 바꾼다. 100자쯤에서 접어 쓴
    md를 그대로 올리면 문장이 중간에서 끊긴다. 표·코드블록·헤딩·리스트·인용은
    줄 구조가 의미이므로 건드리지 않는다.
    """
    out, in_fence = [], False
    for line in text.split('\n'):
        if line.strip().startswith('```'):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        if (out and out[-1].strip()
                and not is_struct(line)
                and not _NO_JOIN_AFTER.match(out[-1].strip())):
            out[-1] = out[-1].rstrip() + ' ' + line.strip()
        else:
            out.append(line)
    return '\n'.join(out)


def strip_frontmatter(text):
    """frontmatter를 떼고 (본문, title 필드) 를 돌려준다."""
    if not text.startswith('---\n'):
        return text, None
    try:
        end = text.index('\n---\n', 3)
    except ValueError:
        return text, None
    fm, body = text[4:end], text[end + 5:]
    m = re.search(r'^title:\s*(.+?)\s*$', fm, re.M)
    title = None
    if m:
        title = m.group(1)
        # YAML 바깥 따옴표만 벗긴다 (제목 안의 " 는 보존)
        if len(title) > 1 and title[0] == title[-1] and title[0] in "'\"":
            title = title[1:-1]
    return body, title


def main():
    if len(sys.argv) < 3:
        sys.stderr.write(__doc__)
        return 2
    src, out_dir = sys.argv[1], sys.argv[2]
    slug = None
    if '--slug' in sys.argv:
        slug = sys.argv[sys.argv.index('--slug') + 1]

    raw = io.open(src, encoding='utf-8', newline='').read()
    text = raw.replace('\r\n', '\n').replace('\r', '\n')
    original = text

    # 1) frontmatter
    text, title = strip_frontmatter(text)
    text = text.lstrip('\n')

    # 2) H1 -> 제목 (frontmatter title 이 있으면 그쪽이 우선)
    m = re.match(r'#[ \t]+(.+?)\n', text)
    if m:
        title = title or m.group(1).strip()
        text = text[m.end():].lstrip('\n')

    # 3) 이미지 슬롯 제거 (+ 삽입 위치 기록)
    lines = text.split('\n')
    slots = []
    for i, l in enumerate(lines):
        if '{이미지:' not in l:
            continue
        prev = next((lines[j].strip() for j in range(i - 1, max(-1, i - 5), -1)
                     if lines[j].strip()), '')
        nxt = next((lines[j].strip() for j in range(i + 1, min(len(lines), i + 5))
                    if lines[j].strip()), '')
        slots.append({'slot': l.strip(), 'after': prev[:100], 'before': nxt[:100]})
    if slots:
        lines = [l for l in lines if '{이미지:' not in l]
        text = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines))

    # 4) 소프트 줄바꿈 합치기
    text = unwrap(text)

    # 5) 구조 검증 — 하나라도 어긋나면 쓰지 않는다
    before, after = count(original), count(text)
    drift = {k: [before[k], after[k]] for k in before if before[k] != after[k]}
    if drift:
        sys.stderr.write('구조가 변했다. 파일을 쓰지 않는다:\n')
        for k, (b, a) in drift.items():
            sys.stderr.write('  %-12s %d -> %d\n' % (k, b, a))
        return 1

    # 6) 남아 있으면 안 되는 것
    must_be_zero = {
        'frontmatter': len(re.findall(r'^stage:', text, re.M)),
        'h1': len(re.findall(r'^# ', text, re.M)),
        'wikilink': text.count('[['),
        'image_slot': text.count('{이미지'),
        'cite_marker': len(re.findall(r'cite\w*turn', text)),
        'cr': text.count('\r'),
        'rel_link': len(re.findall(r'\]\(\.{1,2}/', text)),
    }
    leftover = {k: v for k, v in must_be_zero.items() if v}
    if leftover:
        sys.stderr.write('제거되지 않은 항목이 있다: %s\n' % leftover)
        return 1

    if not slug:
        slug = os.path.splitext(os.path.basename(src))[0][:40]

    body_path = os.path.join(out_dir, '%s-발행용.md' % slug)
    meta_path = os.path.join(out_dir, '%s-발행.json' % slug)
    io.open(body_path, 'w', encoding='utf-8', newline='').write(text)

    meta = {
        'title': title,
        'body_path': os.path.abspath(body_path),
        'source_draft': os.path.abspath(src),
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'chars': len(text),
        'lines': len(text.split('\n')),
        'counts': after,
        'must_be_zero': must_be_zero,
        'first_line': text.split('\n')[0][:120],
        'links': re.findall(r'\]\((https?://[^)]+)\)', text),
        'image_slots_removed': slots,
        'visibility': '비공개',
    }
    io.open(meta_path, 'w', encoding='utf-8', newline='').write(
        json.dumps(meta, ensure_ascii=False, indent=2) + '\n')

    out = sys.stdout
    out.write('발행용 본문: %s\n' % body_path)
    out.write('매니페스트  : %s\n' % meta_path)
    out.write('제목        : %s\n' % title)
    out.write('%d줄 / %d자 / 링크 %d개\n' % (meta['lines'], meta['chars'], after['links']))
    out.write('구조 보존   : H2 %(h2)d · H3 %(h3)d · 표 %(table_pipes)d · '
              '인용 %(quotes)d · 리스트 %(lists)d · 코드펜스 %(code_fences)d\n' % after)
    if slots:
        out.write('\n제거한 이미지 슬롯 %d개 (에디터에서 직접 삽입):\n' % len(slots))
        for i, s in enumerate(slots, 1):
            out.write('  %d) %s\n     ↑ %s\n' % (i, s['slot'], s['after']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
