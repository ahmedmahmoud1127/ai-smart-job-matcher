"""Inline SVG artwork for the login page: logo mark, feature icons and the AI robot scene.

Everything is hand-drawn vector (no external images) so it stays sharp and loads instantly.
NOTE: strings are kept free of blank lines / leading indentation so Markdown never turns them into code blocks.
"""


def logo_mark(size: int = 56, uid: str = "a") -> str:
    """Purple briefcase with an orbit ring and a gold sparkle (brand mark)."""
    g = f"lgLogo{uid}"
    return (
        f'<svg class="lg-logo-mark" width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6D4BEA"/><stop offset="1" stop-color="#3D2FB5"/></linearGradient></defs>'
        f'<path d="M24 20v-4a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v4" fill="none" stroke="#3D2FB5" stroke-width="4" stroke-linecap="round"/>'
        f'<rect x="8" y="19" width="48" height="34" rx="9" fill="url(#{g})"/>'
        f'<rect x="8" y="19" width="48" height="12" rx="6" fill="#fff" opacity=".14"/>'
        f'<rect x="27" y="32" width="10" height="9" rx="2.5" fill="#fff"/>'
        f'<ellipse cx="32" cy="38" rx="31" ry="9" fill="none" stroke="#C7D2FE" stroke-width="2.4" transform="rotate(-14 32 38)" opacity=".9"/>'
        f'<path d="M54 8c.5 4 1.6 5.2 5.5 5.7-3.9.6-5 1.8-5.5 5.8-.5-4-1.6-5.2-5.5-5.8C52.4 13.2 53.5 12 54 8z" fill="#FBBF24"/>'
        '</svg>')


_ICONS = {
    "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7z" fill="#3B82F6" stroke="#3B82F6" stroke-width="1.2" stroke-linejoin="round"/>',
    "chart": ('<rect x="3" y="13" width="4" height="8" rx="1" fill="#3B6FF0"/><rect x="10" y="9" width="4" height="12" rx="1" fill="#3B6FF0"/>'
              '<rect x="17" y="5" width="4" height="16" rx="1" fill="#3B6FF0"/><path d="m3 9 6-5 5 3 6-5" fill="none" stroke="#7C3AED" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'),
    "rocket": ('<path d="M14 4c3-1.6 5.6-1.6 6-1.2.4.4.4 3-1.2 6l-5 5-3.8-3.8z" fill="#8B5CF6"/><path d="m8 10-3.5.8L2.5 14l4 .5M14 16l-.8 3.5L10 21.5 9.5 17.5" fill="none" stroke="#6D4BEA" stroke-width="1.6" stroke-linejoin="round"/>'
               '<circle cx="15.5" cy="8.5" r="1.6" fill="#fff"/><path d="m5 19-2 2M4 16l-1.5 1.5M8 20l-1.5 1.5" stroke="#F59E0B" stroke-width="1.6" stroke-linecap="round"/>'),
}


def feature_icon(name: str) -> str:
    return f'<svg width="22" height="22" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{_ICONS[name]}</svg>'


# 4-point sparkle centred on (0,0); reused with <use>-free copies to keep the sanitizer happy.
_SPARK = "M0 -14 Q2 -2 14 0 Q2 2 0 14 Q-2 2 -14 0 Q-2 -2 0 -14z"

ROBOT_SCENE = f"""<svg class="lg-art" viewBox="0 0 1000 940" preserveAspectRatio="xMaxYMax meet" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Friendly AI robot with a graduation cap holding a laptop, next to a magnifying glass and a Software Developer job card">
<defs>
<radialGradient id="lgGlow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".6" stop-color="#E9E5FF" stop-opacity=".45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="lgWhite" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".6" stop-color="#EEF0FF"/><stop offset="1" stop-color="#CDD3F6"/></linearGradient>
<linearGradient id="lgNavy" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#363C9A"/><stop offset="1" stop-color="#171B58"/></linearGradient>
<linearGradient id="lgVisor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#171D52"/><stop offset="1" stop-color="#050720"/></linearGradient>
<linearGradient id="lgCap" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2C3085"/><stop offset="1" stop-color="#14174F"/></linearGradient>
<linearGradient id="lgPurple" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9B6CFF"/><stop offset="1" stop-color="#5B3FD6"/></linearGradient>
<linearGradient id="lgGlass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".92"/><stop offset="1" stop-color="#E4E8FF" stop-opacity=".6"/></linearGradient>
<linearGradient id="lgLens" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#C9D3FF" stop-opacity=".35"/></linearGradient>
<linearGradient id="lgPlat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D8D6FB"/><stop offset="1" stop-color="#A9A8EE"/></linearGradient>
<linearGradient id="lgBuild" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8E9DF0" stop-opacity=".55"/><stop offset="1" stop-color="#C9D2FA" stop-opacity=".15"/></linearGradient>
<linearGradient id="lgLeaf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5CC9B5"/><stop offset="1" stop-color="#2E8F9C"/></linearGradient>
<filter id="lgGlowF" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="lgShadow" x="-20%" y="-20%" width="140%" height="160%"><feGaussianBlur stdDeviation="10"/></filter>
</defs>
<g opacity=".95"><ellipse cx="170" cy="430" rx="95" ry="26" fill="#fff" opacity=".55"/><ellipse cx="120" cy="448" rx="80" ry="24" fill="#fff" opacity=".55"/><ellipse cx="960" cy="330" rx="90" ry="26" fill="#fff" opacity=".5"/></g>
<g fill="url(#lgBuild)"><rect x="405" y="560" width="62" height="280" rx="4"/><rect x="470" y="470" width="78" height="370" rx="4"/><rect x="552" y="590" width="58" height="250" rx="4"/><rect x="858" y="440" width="70" height="400" rx="4"/><rect x="932" y="520" width="68" height="320" rx="4"/><path d="M880 440 904 372 928 440z"/></g>
<circle cx="745" cy="420" r="340" fill="url(#lgGlow)"/>
<ellipse cx="520" cy="915" rx="500" ry="78" fill="url(#lgPlat)"/>
<ellipse cx="520" cy="885" rx="470" ry="56" fill="#E2E0FC"/>
<ellipse cx="520" cy="880" rx="440" ry="44" fill="#ECEBFF"/>
<ellipse cx="770" cy="866" rx="150" ry="20" fill="#6D6FD0" opacity=".28" filter="url(#lgShadow)"/>
<g class="lg-plant" fill="url(#lgLeaf)"><path d="M10 940C-10 860 20 790 70 760c10 60-10 120-60 180z"/><path d="M60 940c-20-70 0-130 52-170 14 56 0 116-52 170z" opacity=".85"/><path d="M0 800c40 0 70 20 90 60-50 6-84-10-90-60z" opacity=".8"/></g>
<g class="lg-plant" fill="url(#lgLeaf)" opacity=".9"><path d="M1000 940c-28-60-18-120 20-160 20 60 14 120-20 160z"/><path d="M960 940c-24-50-16-100 20-136 18 50 8 100-20 136z" opacity=".8"/></g>
<g class="lg-float2">
<g transform="translate(212,878) rotate(0)"><path d="M0 0 82-86" stroke="#232C8C" stroke-width="38" stroke-linecap="round" fill="none"/><path d="M-4 -4 78-86" stroke="#3E4BC6" stroke-width="8" stroke-linecap="round" fill="none" opacity=".55" transform="translate(-6,-6)"/></g>
<circle cx="370" cy="730" r="96" fill="url(#lgLens)" stroke="#2B3496" stroke-width="28"/>
<circle cx="370" cy="730" r="82" fill="none" stroke="#6B7BFF" stroke-width="3" opacity=".5"/>
<path d="M305 705a70 70 0 0 1 52-52" stroke="#fff" stroke-width="9" fill="none" stroke-linecap="round" opacity=".9"/>
<circle cx="322" cy="778" r="6" fill="#fff" opacity=".8"/>
</g>
<g class="lg-robot"><g transform="translate(-22,0)">
<g class="lg-legs"><rect x="696" y="630" width="58" height="190" rx="29" fill="url(#lgWhite)" stroke="#C3C9F1" stroke-width="2.5"/><rect x="786" y="630" width="58" height="200" rx="29" fill="url(#lgWhite)" stroke="#C3C9F1" stroke-width="2.5"/><ellipse cx="718" cy="826" rx="52" ry="26" fill="url(#lgNavy)"/><ellipse cx="826" cy="840" rx="56" ry="26" fill="url(#lgNavy)"/></g>
<rect x="662" y="418" width="200" height="240" rx="80" fill="url(#lgWhite)" stroke="#C3C9F1" stroke-width="2.5"/>
<ellipse cx="722" cy="470" rx="46" ry="30" fill="#fff" opacity=".7"/>
<rect x="692" y="620" width="140" height="36" rx="18" fill="url(#lgNavy)"/>
<rect x="716" y="452" width="98" height="78" rx="22" fill="url(#lgNavy)" stroke="#3B82F6" stroke-width="4"/>
<text x="765" y="510" text-anchor="middle" font-size="46" font-weight="800" fill="#38BDF8" filter="url(#lgGlowF)">AI</text>
<rect x="722" y="384" width="80" height="46" rx="16" fill="url(#lgNavy)"/>
<g class="lg-arm-l"><path d="M680 474 630 508" stroke="#C3C9F1" stroke-width="50" stroke-linecap="round" fill="none"/><path d="M680 474 630 508" stroke="#F3F4FF" stroke-width="42" stroke-linecap="round" fill="none"/><circle cx="680" cy="474" r="30" fill="url(#lgNavy)"/><circle cx="630" cy="508" r="24" fill="url(#lgNavy)"/><path d="M630 508 592 452" stroke="#C3C9F1" stroke-width="46" stroke-linecap="round" fill="none"/><path d="M630 508 592 452" stroke="#F3F4FF" stroke-width="38" stroke-linecap="round" fill="none"/><path d="M584 432 556 386" stroke="#1E2266" stroke-width="22" stroke-linecap="round" fill="none"/><circle cx="584" cy="446" r="34" fill="#F6F7FF" stroke="#C3C9F1" stroke-width="3"/><circle cx="598" cy="452" r="12" fill="#E3E6FA"/></g>
<g class="lg-arm-r"><path d="M846 478 888 566" stroke="#C3C9F1" stroke-width="50" stroke-linecap="round" fill="none"/><path d="M846 478 888 566" stroke="#F3F4FF" stroke-width="42" stroke-linecap="round" fill="none"/><circle cx="846" cy="478" r="30" fill="url(#lgNavy)"/><circle cx="888" cy="566" r="24" fill="url(#lgNavy)"/></g>
<g transform="rotate(-7 885 565)"><rect x="776" y="498" width="204" height="152" rx="18" fill="#10143F" opacity=".35" transform="translate(6,10)"/><rect x="776" y="498" width="204" height="152" rx="18" fill="url(#lgNavy)" stroke="#4F8BFF" stroke-width="3"/><rect x="786" y="508" width="184" height="132" rx="12" fill="none" stroke="#6B8CFF" stroke-width="1.5" opacity=".5"/><g filter="url(#lgGlowF)" stroke="#38BDF8" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="847" y="556" width="62" height="44" rx="9"/><path d="M866 556v-8a6 6 0 0 1 6-6h10a6 6 0 0 1 6 6v8M847 574h62"/></g><rect x="772" y="646" width="212" height="14" rx="7" fill="#0C1038"/></g>
<g><circle cx="884" cy="642" r="34" fill="#F6F7FF" stroke="#C3C9F1" stroke-width="3"/></g>
<g class="lg-head">
<circle cx="628" cy="302" r="48" fill="#3B82F6"/><circle cx="628" cy="302" r="37" fill="url(#lgNavy)"/><circle cx="628" cy="302" r="22" fill="#60A5FA" opacity=".55" filter="url(#lgGlowF)"/>
<circle cx="892" cy="302" r="48" fill="#3B82F6"/><circle cx="892" cy="302" r="37" fill="url(#lgNavy)"/><circle cx="892" cy="302" r="22" fill="#60A5FA" opacity=".55" filter="url(#lgGlowF)"/>
<rect x="630" y="192" width="260" height="208" rx="98" fill="url(#lgWhite)" stroke="#C3C9F1" stroke-width="2.5"/>
<path d="M662 214c40-22 150-22 190 0" stroke="#fff" stroke-width="10" stroke-linecap="round" fill="none" opacity=".8"/>
<rect x="656" y="234" width="208" height="128" rx="58" fill="url(#lgVisor)"/>
<path d="M684 252c30-10 120-10 150 0" stroke="#fff" stroke-width="3" stroke-linecap="round" fill="none" opacity=".18"/>
<g class="lg-eyes" fill="none" stroke="#35D4FF" stroke-linecap="round" filter="url(#lgGlowF)"><path d="M694 308q22-42 44 0" stroke-width="13"/><path d="M782 308q22-42 44 0" stroke-width="13"/><path d="M736 332q24 24 48 0" stroke-width="10"/></g>
<path d="M664 190v32q0 20 22 28 74 26 148 0 22-8 22-28v-32z" fill="url(#lgCap)"/>
<polygon points="596,178 744,112 934,198 786,266" fill="url(#lgCap)" stroke="#4B54C8" stroke-width="2.5" stroke-linejoin="round"/>
<polygon points="596,178 744,112 934,198 770,170" fill="#fff" opacity=".1"/>
<circle cx="765" cy="188" r="9" fill="#F2C65A"/>
<path d="M765 188 902 214" stroke="#F2C65A" stroke-width="4.5" stroke-linecap="round" fill="none"/>
<path d="M906 214v58" stroke="#F2C65A" stroke-width="6" stroke-linecap="round"/>
<path d="M892 268h28l5 38h-38z" fill="#F4C84F"/><path d="M898 276l-2 24M906 276v26M914 276l2 24" stroke="#D49B1E" stroke-width="2.4" stroke-linecap="round"/>
<path d="M640 178 620 148M606 196 574 184" stroke="#1E2266" stroke-width="7" stroke-linecap="round" fill="none"/>
</g>
</g>
</g>
<g class="lg-float3">
<g transform="translate(455,675) rotate(5)">
<rect x="26" y="-16" width="300" height="200" rx="24" fill="#fff" opacity=".35"/>
<rect x="0" y="6" width="300" height="190" rx="22" fill="#6D6FD0" opacity=".25" filter="url(#lgShadow)"/>
<rect x="0" y="0" width="300" height="190" rx="22" fill="url(#lgGlass)" stroke="#fff" stroke-width="2"/>
<text x="34" y="52" font-size="24" font-weight="700" fill="#1A1B4B" transform="rotate(3 34 52)">Software Developer</text>
<rect x="34" y="76" width="190" height="9" rx="4.5" fill="#B9BFEA"/><rect x="34" y="98" width="140" height="9" rx="4.5" fill="#CDD2F2"/>
<rect x="34" y="128" width="104" height="38" rx="19" fill="url(#lgPurple)"/>
<path d="M60 139a6.5 6.5 0 1 1 13 0c0 5-6.5 11.5-6.5 11.5S60 144 60 139z" fill="none" stroke="#fff" stroke-width="2.2"/><circle cx="66.5" cy="139" r="2" fill="#fff"/>
<text x="82" y="153" font-size="15" font-weight="700" fill="#fff">Remote</text>
</g>
<g transform="translate(742,772) rotate(-9)"><rect x="0" y="8" width="118" height="100" rx="24" fill="#4B33C4" opacity=".35" filter="url(#lgShadow)"/><rect x="0" y="0" width="118" height="100" rx="24" fill="url(#lgPurple)"/><rect x="0" y="0" width="118" height="38" rx="19" fill="#fff" opacity=".12"/><text x="59" y="66" text-anchor="middle" font-size="46" font-weight="800" fill="#fff">&lt;/&gt;</text></g>
</g>
<g fill="#F5B93A" class="lg-spark"><path d="{_SPARK}" transform="translate(560,300) scale(1.1)"/><path d="{_SPARK}" transform="translate(980,150)"/></g>
<g fill="#fff" class="lg-spark lg-spark2"><path d="{_SPARK}" transform="translate(470,610) scale(.9)"/><path d="{_SPARK}" transform="translate(975,430) scale(1.2)"/><path d="{_SPARK}" transform="translate(690,70) scale(.8)"/></g>
<g fill="#8B5CF6" opacity=".7" class="lg-spark"><circle cx="520" cy="400" r="5"/><circle cx="950" cy="760" r="6"/><circle cx="440" cy="640" r="4"/></g>
</svg>"""
