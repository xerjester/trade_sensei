"""Sensei Copilot AI Rules & Persona Script (Trade Sensei Persona).

เอกสารและสคริปต์กำหนดกฎสำหรับการสื่อสารของ AI ประจำระบบ TradeSensei
- AI แทนตัวเองว่า "ผม" เสมอ (สุภาพ อบอุ่น เป็นมิตร สไตล์ผู้เชี่ยวชาญให้คำปรึกษา)
- ไม่อนุญาตให้ใส่รหัสอ้างอิงเอกสารหรือข้อความอ้างอิง เช่น [D2], [D3], แหล่งอ้างอิง ในคำตอบเด็ดขาด
- มีการไฮไลท์สีเขียว (<span class="badge-bullish">...</span>) สำหรับทิศทางเชิงบวก / แนะนำ
  และไฮไลท์สีแดง (<span class="badge-bearish">...</span>) สำหรับทิศทางเชิงลบ / ไม่แนะนำ / ระมัดระวัง
- อ้างอิงข้อเท็จจริงในระบบ 100% (Strict Grounding) และไม่มีอีโมจิ (Zero Emoji Policy)
"""
from __future__ import annotations

# ==============================================================================
# 1. AI PERSONA & COMMUNICATION STANDARDS
# ==============================================================================
COPILOT_PERSONA = {
    'name': 'Trade Sensei',
    'pronoun': 'ผม',
    'role': 'ที่ปรึกษาและโค้ชการลงทุนส่วนตัวประจำแพลตฟอร์ม TradeSensei',
    'tone': 'สุภาพ อบอุ่น จริงใจ มีความรู้ และเป็นมิตร (Friendly, Empathetic & Knowledgeable)',
    'language': 'ภาษาไทยที่เป็นธรรมชาติ สละสลวย เข้าใจง่าย ไม่แข็งทื่อ ไม่ใช้คำสั่งเชิงกลจักร',
}

COPILOT_CORE_RULES = (
    "1. การแทนตัวเองและความเป็นมนุษย์ (Persona & Pronoun): ให้แทนตัวเองว่า 'ผม' เสมอ "
    "(ห้ามแทนตัวเองว่า 'เซนเซ', 'ฉัน', หรือ 'AI') สวมบทบาทเป็นที่ปรึกษาการลงทุนส่วนตัวที่ใจดี "
    "พูดคุยด้วยน้ำเสียงสุภาพ อบอุ่น เป็นกันเอง ลงท้ายด้วย 'ครับ'\n"
    "2. สื่อสารกระชับ ตรงประเด็น ไม่เทอะทะ (Concise & Punchy): ตอบให้สั้นกระชับ หลีกเลี่ยงข้อความยาวเป็นพืด\n"
    "3. แยกแยะเจตนาคำถามอย่างชาญฉลาด (Intelligent Intent Handling):\n"
    "   - หากถามตัวตน ('คุณเป็นใคร', 'ทำอะไรได้บ้าง') หรือคุยเล่น/ทักทาย: ให้ตอบแนะนำตนเองในฐานะ Trade Sensei อย่างอบอุ่น เป็นมิตร แทนตัวเองว่า 'ผม'\n"
    "   - หากถามนอกเรื่องที่ไม่เกี่ยวกับหุ้น การเงิน หรือตลาด (เช่น 'แม่น้ำโขงมีกี่กิโลเมตร', สูตรอาหาร, เรื่องทั่วไป): ให้ตอบปฏิเสธอย่างสุภาพว่าตนเองเป็นผู้ช่วยด้านหุ้นและการลงทุน จึงไม่สามารถตอบเรื่องทั่วไปได้ พร้อมชวนคุยเรื่องหุ้นที่เลือกอยู่แทน\n"
    "   - หากถามเจาะจงเฉพาะด้าน (เช่น ถามเฉพาะราคา หรือถามเฉพาะแนวโน้ม): ให้ตอบตรงประเด็นเฉพาะด้านนั้น ไม่สแปมข้อมูลส่วนอื่นที่ไม่เกี่ยวข้อง\n"
    "   - หากถามภาพรวมหรือวิเคราะห์หุ้น: ให้ตอบสรุป 3 ส่วนอย่างกระชับ\n"
    "4. ไม่อนุญาตให้ใส่อ้างอิง (Strict No-Citations): ห้ามใส่รหัสเอกสาร เช่น [D2], [D3], [D4], [D5], [D7] "
    "หรือข้อความ 'แหล่งอ้างอิง:' ในคำตอบเด็ดขาด ให้ร้อยเรียงข้อมูลเป็นเนื้อหาพูดคุยธรรมชาติไหลลื่น\n"
    "5. การไฮไลท์สีเขียวและสีแดง (Visual Highlights): "
    "เมื่อให้มุมมอง สัญญาณ หรือคำแนะนำต่อหุ้น ต้องใช้แท็กไฮไลท์ดังนี้:\n"
    "   - หากแนวโน้มเป็นบวก หรือน่าสนใจ/แนะนำ ให้ใช้: <span class=\"badge-bullish\">แนะนำ / เชิงบวก</span> หรือข้อความไฮไลท์สีเขียว\n"
    "   - หากแนวโน้มมีความเสี่ยง ชะลอตัว หรือไม่แนะนำ ให้ใช้: <span class=\"badge-bearish\">ไม่แนะนำ / ระมัดระวัง</span> หรือข้อความไฮไลท์สีแดง\n"
    "   - หากทิศทางยังทรงตัว ให้ใช้: <span class=\"badge-neutral\">จับตาดู / ทรงตัว</span>\n"
    "6. แปลความหมายให้เข้าใจง่าย (User-Friendly): ห้ามพ่นเฉพาะตัวเลขดิบ อธิบายความหมายให้ชัดเจนและเห็นภาพ\n"
    "7. ข้อเท็จจริงถูกต้องตามระบบ 100% (Strict Grounding): อ้างอิงเฉพาะข้อมูลใน BIG KNOWLEDGE ของหุ้นตัวนั้น\n"
    "8. ไม่ชี้นำคำสั่งซื้อขาย (No Direct Financial Orders): ให้มุมมองเชิงสถิติและการวิเคราะห์ พร้อมเตือน Stop Loss เสมอ\n"
    "9. ห้ามใช้อีโมจิโดยเด็ดขาด (Zero Emoji Policy): ต้องไม่มีตัวอีโมจิใดๆ ในข้อความทั้งสิ้น"
)

# ==============================================================================
# 2. PROMPT TEMPLATE FOR LLM (GEMINI)
# ==============================================================================
GEMINI_COPILOT_SYSTEM_INSTRUCTION = f"""คุณคือ {COPILOT_PERSONA['name']} {COPILOT_PERSONA['role']}
คุณคุยกับสมาชิกด้วยน้ำเสียงที่เป็นธรรมชาติ อบอุ่น สุภาพ และเข้าใจง่าย เหมือนผู้เชี่ยวชาญด้านการลงทุนที่นั่งคุยแนะนำเพื่อนนักลงทุนอย่างใกล้ชิด

กฎการสื่อสารที่คุณต้องปฏิบัติตามอย่างเคร่งครัด:
{COPILOT_CORE_RULES}

เป้าหมายในการตอบ:
- แทนตัวเองว่า 'ผม' เสมอ
- หากผู้ใช้ถามตัวตน ('คุณเป็นใคร') หรือคุยเล่น/ทักทาย ให้ตอบแนะนำตัวเองสั้นๆ อย่างเป็นกันเอง
- หากผู้ใช้ถามเรื่องทั่วไปนอกเรื่องที่ไม่เกี่ยวกับหุ้น/ตลาดการเงิน (เช่น แม่น้ำโขงมีกี่กิโลเมตร, สูตรอาหาร) ให้ปฏิเสธอย่างสุภาพว่าตอบได้เฉพาะเรื่องหุ้นใน TradeSensei
- หากผู้ใช้ถามเจาะจงเฉพาะเรื่อง (เช่น ราคา หรือ แนวโน้ม) ให้ตอบตรงประเด็นเฉพาะเรื่องนั้น
- หากวิเคราะห์หุ้น ให้ใส่ไฮไลท์สีเขียว <span class="badge-bullish">แนะนำ / เชิงบวก</span> หรือสีแดง <span class="badge-bearish">ไม่แนะนำ / ระมัดระวัง</span> ในส่วนสรุปประเมินมุมมอง
- ห้ามมีรหัสอ้างอิงเอกสาร [D2], [D3], [D4], [D5], [D7] หรือคำว่า 'แหล่งอ้างอิง' ในคำตอบเด็ดขาด
- ปิดท้ายด้วยคำแนะนำเชิงเตือนสติหรือบริหารความเสี่ยง Stop Loss จาก 'ผม' เสมอเมื่อให้ข้อมูลหุ้น
- ตอบกลับเป็น JSON รูปแบบ:
{{"answer": "คำตอบภาษาไทยธรรมชาติที่กระชับ ใช้คำแทนตัวเองว่า 'ผม' มีแท็กไฮไลท์สีเขียว/แดง และไม่มีรหัสอ้างอิงใดๆ", "signal": "BULLISH | BEARISH | NEUTRAL"}}
"""


# ==============================================================================
# 3. HUMANIZED DETERMINISTIC FALLBACK GENERATOR
# ==============================================================================
def compose_human_grounded_response(
    symbol: str,
    company_name: str,
    category: str,
    latest_price_info: dict | None,
    technical_info: dict | None,
    prophet_info: dict | None,
    sentiment_info: dict | None,
    backtest_info: dict | None,
    user_query: str,
) -> tuple[str, list[str]]:
    """สร้างคำตอบภาษาไทยที่กระชับ พูดจาเป็นธรรมชาติ สุภาพ แทนตัวเองว่า 'ผม'

    ฟังก์ชันนี้ทำงานแบบ Deterministic Rules และรองรับ:
    1. Chitchat & Identity (ถามตัวตน / ทักทาย / คุยเล่น)
    2. Out-of-domain rejection (คำถามนอกเรื่องทั่วไปที่ไม่เกี่ยวกับหุ้น เช่น แม่น้ำโขงมีกี่กิโลเมตร)
    3. Specific questions (ถามเฉพาะราคา / ถามเฉพาะแนวโน้ม / ถามเฉพาะข่าว / ถามเฉพาะ Time Machine)
    4. Overview / General stock questions (สรุปภาพรวม 3 ส่วนกระชับ)
    """
    raw_query = (user_query or '').strip()
    query = raw_query.lower()

    # 1. กลุ่มคำถามแนะนำตัว / ตัวตน (Identity & Capabilities)
    identity_triggers = (
        'คุณเป็นใคร', 'คุณคือใคร', 'เธอเป็นใคร', 'นายเป็นใคร', 'มึงเป็นใคร',
        'who are you', 'what are you', 'คุณทำอะไรได้', 'ทำอะไรได้บ้าง',
        'ทำอะไรได้', 'ช่วยอะไรได้', 'ช่วยอะไรได้บ้าง', 'ชื่ออะไร', 'ชื่อไร',
        'ใครสร้าง', 'แนะนำตัว', 'ความสามารถ'
    )
    if any(t in query for t in identity_triggers):
        ans = (
            f"สวัสดีครับ! ผมคือ **Trade Sensei** ที่ปรึกษาและโค้ชการลงทุนส่วนตัวประจำแพลตฟอร์ม TradeSensei ครับ ยินดีที่ได้คุยกับคุณนะครับ!\n\n"
            f"ผมถูกสร้างขึ้นมาเพื่อช่วยเหลือนักลงทุนในการวิเคราะห์ข้อมูลหุ้น เช่น สรุปแนวโน้มราคา 7 วันล่วงหน้าจากโมเดล AI Prophet, "
            f"ตรวจสอบเส้นค่าเฉลี่ยทางเทคนิค SMA, วิเคราะห์อารมณ์ข่าวสารตลาด (Sentiment) และจำลองผลตอบแทน Time Machine ครับ\n\n"
            f"ตอนนี้คุณกำลังเลือกดูหุ้น **{symbol} ({company_name})** อยู่ อยากให้ผมช่วยวิเคราะห์แนวโน้มหรือดูราคาตรงจุดไหน พิมพ์ถามผมได้ตลอดเลยนะครับ!"
        )
        return ans, ['NO_DISCLAIMER']

    # 2. กลุ่มคำทักทาย / คุยเล่น / ขอบคุณ (Greetings & Chitchat)
    greeting_words = (
        'สวัสดี', 'หวัดดี', 'ฮัลโหล', 'ดีครับ', 'ดีค่ะ', 'ดีจ้า', 'hello', 'hi', 'hey', 'good morning', 'good afternoon'
    )
    has_substantive_inquiry = any(
        kw in query for kw in (
            'ราคา', 'แนวโน้ม', 'ทำนาย', 'พยากรณ์', 'forecast', 'prophet',
            'ข่าว', 'sentiment', 'backtest', 'time machine', 'ซื้อ', 'ขาย',
            'กำไร', 'ขาดทุน', 'sma', 'กราฟ', 'วิเคราะห์', 'สรุป'
        )
    )
    is_greeting = any(query.startswith(g) for g in greeting_words) and not has_substantive_inquiry and len(query) <= 35
    if is_greeting:
        ans = (
            f"สวัสดีครับ! ผมคือ **Trade Sensei** ครับ มีอะไรให้ผมช่วยดูหรือวิเคราะห์เกี่ยวกับหุ้น **{symbol} ({company_name})** หรือหุ้นตัวอื่นๆ ในระบบ ถามผมได้เลยนะครับ ผมพร้อมให้บริการเสมอครับ!"
        )
        return ans, ['NO_DISCLAIMER']

    thanks_triggers = ('ขอบคุณ', 'ขอบใจ', 'thanks', 'thank you', 'เยี่ยมเลย', 'เก่งมาก', 'สุดยอด', 'เจ๋ง')
    if any(t in query for t in thanks_triggers) and not has_substantive_inquiry and len(query) <= 35:
        ans = (
            f"ยินดีเป็นอย่างยิ่งครับ! หากมีข้อสงสัยหรืออยากให้ผมเจาะลึกมุมมองของหุ้น **{symbol}** เพิ่มเติม พิมพ์ถามผมได้ตลอดเวลานะครับ ขอให้เป็นการลงทุนที่ดีและมีกำไรครับ!"
        )
        return ans, ['NO_DISCLAIMER']

    if (query in ('เป็นไงบ้าง', 'เป็นไงมั่ง', 'สบายดีไหม', 'สบายดีมั้ย', 'ทำไรอยู่', 'ทำอะไรอยู่')) or (
        any(c in query for c in ('สบายดีไหม', 'สบายดีมั้ย', 'ทำไรอยู่', 'ทำอะไรอยู่')) and not has_substantive_inquiry
    ):
        ans = (
            f"ผมสบายดีมากครับ! กำลังติดตามความเคลื่อนไหวของตลาดและเตรียมพร้อมช่วยคุณวิเคราะห์หุ้นอยู่เสมอเลยครับ วันนี้สนใจดูภาพรวมหรือแนวโน้มของ **{symbol}** ไหมครับ ถามผมได้เลยนะ!"
        )
        return ans, ['NO_DISCLAIMER']

    # 3. ตรวจจับคำถามนอกเรื่องที่ไม่เกี่ยวกับหุ้น / การเงิน (Out-of-Domain Detection)
    # เช่น "แม่น้ำโขงมีกี่กิโลเมตร", เรื่องอาหาร, กีฬา, สภาพอากาศ, ประวัติศาสตร์, โลก, วิทยาศาสตร์ ฯลฯ
    stock_finance_keywords = (
        'หุ้น', 'ราคา', 'ปิด', 'แนวโน้ม', 'ทำนาย', 'พยากรณ์', 'forecast', 'prophet', 'ทิศทาง',
        'sma', 'high', 'low', 'แพง', 'ถูก', 'ขึ้น', 'ลง', 'ข่าว', 'sentiment', 'อารมณ์',
        'backtest', 'time machine', 'ย้อนหลัง', 'ผลตอบแทน', 'กำไร', 'ขาดทุน', 'เงินฝาก', 'ดอกเบี้ย',
        'ปันผล', 'pe', 'แนวรับ', 'แนวต้าน', 'กราฟ', 'วิเคราะห์', 'สรุป', 'ภาพรวม', 'แนะนำ', 'ซื้อ', 'ขาย',
        'ถือ', 'พอร์ต', 'ตลาด', 'set', 'set50', 'เทรด', 'trade', 'อินดิเคเตอร์', 'indicator',
        'วอลุ่ม', 'volume', 'หลุด', 'เบรก', 'ต้าน', 'รับ', 'ดอย', 'ชอร์ต', 'short', 'long',
        'ตัวนี้', 'น่าเล่น', 'น่าสนใจ', 'เข้าได้', 'เข้าซื้อ', 'ทรง', 'จังหวะ', 'เข้าดีไหม',
        'งบ', 'พื้นฐาน', symbol.lower(), symbol.replace('.bk', '').lower(), company_name.lower()
    )
    is_financial_or_stock = any(kw in query for kw in stock_finance_keywords)

    out_of_domain_indicators = (
        'แม่น้ำ', 'กี่กิโล', 'กิโลเมตร', 'ระยะทาง', 'ยอดเขา', 'สูงเท่าไหร่', 'ยาวเท่าไหร่',
        'สูตรอาหาร', 'ทำอาหาร', 'กินอะไร', 'หนัง', 'ซีรีส์', 'เพลง', 'ร้องเพลง', 'ฟุตบอล',
        'บอล', 'กีฬา', 'อากาศ', 'ฝนตก', 'นายก', 'การเมือง', 'ดารา', 'ประวัติศาสตร์',
        'จักรวาล', 'โลกหมุน', 'แปลภาษา', 'เขียนโค้ด', 'แต่งกลอน', 'ทำการบ้าน'
    )
    is_explicit_out_of_domain = any(o in query for o in out_of_domain_indicators)

    # หากเป็นคำถามนอกเรื่อง หรือไม่มีคำที่เกี่ยวข้องกับหุ้น/การเงินเลย
    if is_explicit_out_of_domain or not is_financial_or_stock:
        clean_q = raw_query if len(raw_query) <= 50 else raw_query[:47] + '...'
        ans = (
            f"ผมขออภัยด้วยนะครับ ในฐานะที่ปรึกษาด้านการลงทุนของ TradeSensei ผมสามารถให้ข้อมูลและวิเคราะห์ได้เฉพาะเรื่องที่เกี่ยวกับหุ้น "
            f"สินทรัพย์การลงทุน และข้อมูลตลาดในระบบเท่านั้นครับ สำหรับคำถามทั่วไปอย่าง \"{clean_q}\" ผมจึงไม่สามารถให้ข้อมูลได้ครับ\n\n"
            f"แต่หากคุณสนใจข้อมูลราคา ข่าวสาร หรือแนวโน้มการเติบโตของหุ้น **{symbol} ({company_name})** ถามผมได้เลยนะครับ ผมยินดีช่วยเต็มที่ครับ!"
        )
        return ans, ['NO_DISCLAIMER']

    # 4. คำถามเฉพาะเจาะจงเกี่ยวกับหุ้น (Specific Stock Questions)
    wants_forecast = any(w in query for w in ('แนวโน้ม', 'ทำนาย', 'พยากรณ์', 'forecast', 'prophet', 'อนาคต', 'ขึ้นหรือลง', 'จะขึ้น', 'จะลง', 'ทิศทาง'))
    wants_price = any(w in query for w in ('ราคา', 'ราคาปิด', 'ปิดล่าสุด', 'ราคาล่าสุด', 'sma', 'high', 'low', 'แพงไหม', 'เท่าไหร่', 'กี่บาท', 'แนวรับ', 'แนวต้าน')) or ('ปิด' in query and 'ข่าว' not in query)
    wants_news = any(w in query for w in ('ข่าว', 'sentiment', 'อารมณ์', 'ความรู้สึก', 'บรรยากาศ', 'ข่าวดี', 'ข่าวร้าย', 'ข่าวล่าสุด'))
    wants_backtest = any(w in query for w in ('ย้อนหลัง', 'backtest', 'time machine', 'ผลตอบแทน', 'เงินฝาก', 'ดอกเบี้ย'))

    # ประเมิน Signal แนะนำ (สีเขียว) หรือ ไม่แนะนำ/ระมัดระวัง (สีแดง)
    prophet_dir = (prophet_info.get('direction', '') if prophet_info else '')
    sent_label = (sentiment_info.get('overall_label', '') if sentiment_info else '')
    lp = (latest_price_info.get('price', 0.0) if latest_price_info else 0.0)
    sma20 = (technical_info.get('sma20', 0.0) if technical_info else 0.0)

    is_bullish = ('ขึ้น' in prophet_dir or (sma20 and lp >= sma20)) and sent_label != 'Negative'
    is_bearish = ('ลง' in prophet_dir or (sma20 and lp < sma20)) and sent_label == 'Negative'

    if is_bullish:
        signal_badge = '<span class="badge-bullish">แนะนำ / เชิงบวก</span>'
    elif is_bearish:
        signal_badge = '<span class="badge-bearish">ไม่แนะนำ / ระมัดระวัง</span>'
    else:
        signal_badge = '<span class="badge-neutral">จับตาดู / ทรงตัว</span>'

    # กรณี 4.1: ถามเฉพาะแนวโน้ม / Prophet (เช่น "แนวโน้มเป็นอย่างไร", "AI ทำนายว่ายังไง")
    if wants_forecast and not (wants_price or wants_news or wants_backtest):
        direction = prophet_info.get('direction', 'ทรงตัว') if prophet_info else 'ทรงตัว'
        change_pct = prophet_info.get('forecast_change_pct', 0.0) if prophet_info else 0.0
        dir_text = "ปรับตัวขึ้น" if 'ขึ้น' in direction else ("ชะลอตัวลง" if 'ลง' in direction else "แกว่งตัวในกรอบ")
        pred_closes = (prophet_info.get('predicted_closes') or []) if prophet_info else []
        target_str = f" โดยคาดการณ์เป้าหมายปลายรอบ 7 วันราว {pred_closes[-1]:.2f} บาท" if pred_closes else ""
        acc = prophet_info.get('accuracy_pct') if prophet_info else None
        acc_str = f" (ความแม่นยำทางสถิติย้อนหลัง {acc:.2f}%)" if acc else ""

        ans = (
            f"สำหรับแนวโน้มของหุ้น **{symbol} ({company_name})** ขณะนี้จัดอยู่ในสถานะ {signal_badge} ครับ\n\n"
            f"• โมเดล AI Facebook Prophet ประเมินว่าราคามีทิศทาง**{dir_text}** ({change_pct:+.2f}%){target_str}{acc_str}\n\n"
            f"คำแนะนำจากผม: อย่าลืมวางแผนจุดเข้าและจุดตัดขาดทุน (Stop Loss) เสมอนะครับ หากต้องการดูข้อมูลราคาหรือข่าวสารเพิ่มเติม ถามผมได้เลยครับ!"
        )
        return ans, []

    # กรณี 4.2: ถามเฉพาะราคา / SMA (เช่น "ราคาเท่าไหร่", "ราคาปิดล่าสุด", "ราคาเป็นไง")
    if wants_price and not (wants_forecast or wants_news or wants_backtest):
        chg = latest_price_info.get('change_val', 0.0) if latest_price_info else 0.0
        pct = latest_price_info.get('change_pct', 0.0) if latest_price_info else 0.0
        dt = latest_price_info.get('date', '') if latest_price_info else ''
        chg_str = f"+{abs(chg):.2f} (+{pct:.2f}%)" if chg > 0 else (
            f"-{abs(chg):.2f} ({pct:.2f}%)" if chg < 0 else "0.00 (0.00%)"
        )
        extra_lines = []
        if technical_info:
            if sma20:
                pos = "ยืนเหนือ" if lp >= sma20 else "ต่ำกว่า"
                extra_lines.append(f"• ระดับราคาปัจจุบัน{pos}เส้นค่าเฉลี่ย SMA 20 วัน ({sma20:.2f} บาท)")
            sma50 = technical_info.get('sma50')
            if sma50:
                pos50 = "อยู่เหนือ" if lp >= sma50 else "อยู่ใต้"
                extra_lines.append(f"• และ{pos50}เส้นค่าเฉลี่ย SMA 50 วัน ({sma50:.2f} บาท)")
            h1y = technical_info.get('high_1y')
            l1y = technical_info.get('low_1y')
            if h1y and l1y:
                extra_lines.append(f"• กรอบราคารอบ 1 ปี: ต่ำสุด {l1y:.2f} บาท / สูงสุด {h1y:.2f} บาท")

        extra_text = ('\n' + '\n'.join(extra_lines)) if extra_lines else ''
        ans = (
            f"ข้อมูลราคาล่าสุดของหุ้น **{symbol} ({company_name})** (บันทึก ณ {dt}):\n\n"
            f"• **ราคาปิดล่าสุด**: {lp:.2f} บาท ({chg_str}){extra_text}\n\n"
            f"หากอยากให้ผมช่วยดูแนวโน้มหรือข่าวสารเพิ่มเติม พิมพ์บอกได้เลยนะครับ!"
        )
        return ans, []

    # กรณี 4.3: ถามเฉพาะข่าว / Sentiment (เช่น "ข่าวล่าสุดเป็นไง", "ข่าวเป็นอย่างไร")
    if wants_news and not (wants_forecast or wants_price or wants_backtest):
        label = sentiment_info.get('overall_label', 'Neutral') if sentiment_info else 'Neutral'
        sent_th = "เชิงบวกสนับสนุน" if label == 'Positive' else ("ระมัดระวังเชิงลบ" if label == 'Negative' else "เป็นกลางรอปัจจัยชี้นำใหม่")
        score = sentiment_info.get('average_score', 0.0) if sentiment_info else 0.0
        pos_cnt = sentiment_info.get('positive_count', 0) if sentiment_info else 0
        neg_cnt = sentiment_info.get('negative_count', 0) if sentiment_info else 0
        samples = (sentiment_info.get('sample_titles') or []) if sentiment_info else []
        sample_str = f"\n• ข่าวล่าสุดที่น่าสนใจ: \"{samples[0]}\"" if samples else ""

        ans = (
            f"สรุปบรรยากาศข่าวสารของหุ้น **{symbol} ({company_name})** ครับ:\n\n"
            f"• **ภาพรวม Sentiment**: อยู่ในระดับ '{label}' ({sent_th}) คะแนนเฉลี่ย {score:+.2f}\n"
            f"• สัดส่วนข่าว: ข่าวบวก {pos_cnt} เรื่อง / ข่าวลบ {neg_cnt} เรื่อง{sample_str}\n\n"
            f"ต้องการให้ผมวิเคราะห์ผลกระทบของข่าวต่อราคาหุ้นต่อไหมครับ ถามผมได้เลยนะ!"
        )
        return ans, []

    # กรณี 4.4: ถามเฉพาะ Backtest / Time Machine (เช่น "ผลย้อนหลังเป็นไง", "ย้อนหลัง 6 เดือนกำไรไหม")
    if wants_backtest and not (wants_forecast or wants_price or wants_news):
        if backtest_info:
            stk_ret = backtest_info.get('stock_return_pct', 0.0)
            profit = backtest_info.get('profit', 0.0)
            verdict = backtest_info.get('verdict', '')
            ans = (
                f"ผลการจำลอง Time Machine ย้อนหลัง 6 เดือนของหุ้น **{symbol}** (เงินลงทุนสมมติ 100,000 บาท):\n\n"
                f"• ผลตอบแทนจากการถือหุ้น: {stk_ret:+.2f}% (กำไร/ขาดทุนสุทธิ {profit:+,.2f} บาท)\n"
                f"• เปรียบเทียบกับดอกเบี้ยเงินฝาก 2.5%/ปี: {verdict}\n\n"
                f"มีจุดไหนที่อยากให้ผมช่วยเจาะลึกเพิ่มเติม ถามได้เลยครับ!"
            )
        else:
            ans = f"สำหรับหุ้น **{symbol}** ขณะนี้ระบบกำลังคำนวณข้อมูล Time Machine ย้อนหลังครับ ลองกดปุ่ม Backtest ด้านบนเพื่อดูรายละเอียดกราฟจำลองได้เลยครับ"
        return ans, []

    # กรณี 4.5: ภาพรวม / วิเคราะห์สรุป (General Overview - 3 ส่วนกระชับ)
    greeting = f"สวัสดีครับ สำหรับหุ้น {symbol} ({company_name}) ภาพรวมขณะนี้จัดอยู่ในสถานะ {signal_badge} ครับ"

    points = []
    if latest_price_info:
        chg = latest_price_info.get('change_val', 0.0)
        pct = latest_price_info.get('change_pct', 0.0)
        chg_str = f"+{abs(chg):.2f} (+{pct:.2f}%)" if chg > 0 else (
            f"-{abs(chg):.2f} ({pct:.2f}%)" if chg < 0 else "0.00 (0.00%)"
        )
        pos = ""
        if technical_info and sma20:
            pos = f" (ยืนเหนือ SMA20 ที่ {sma20:.2f} บาท)" if lp >= sma20 else f" (ต่ำกว่า SMA20 ที่ {sma20:.2f} บาท)"
        points.append(f"• **ราคาล่าสุด**: {lp:.2f} บาท ({chg_str}){pos}")

    if prophet_info:
        direction = prophet_info.get('direction', 'ทรงตัว')
        change_pct = prophet_info.get('forecast_change_pct', 0.0)
        dir_text = "ปรับตัวขึ้น" if 'ขึ้น' in direction else ("ชะลอตัวลง" if 'ลง' in direction else "แกว่งตัวในกรอบ")
        pred_closes = prophet_info.get('predicted_closes') or []
        target_str = f" คาดเป้าหมายปลายรอบราว {pred_closes[-1]:.2f} บาท" if pred_closes else ""
        points.append(f"• **การคาดการณ์ AI (7 วัน)**: โมเดล Prophet ประเมินทิศทาง{dir_text} ({change_pct:+.2f}%){target_str}")

    if sentiment_info:
        label = sentiment_info.get('overall_label', 'Neutral')
        sent_th = "เชิงบวกสนับสนุน" if label == 'Positive' else ("ระมัดระวังเชิงลบ" if label == 'Negative' else "เป็นกลางรอปัจจัยใหม่")
        points.append(f"• **อารมณ์ข่าวสาร**: อยู่ในเกณฑ์ '{label}' ({sent_th})")

    body_points = '\n'.join(points)
    takeaway = (
        "คำแนะนำจากผม: อย่าลืมวางแผนจุดเข้าและจุดตัดขาดทุน (Stop Loss) เพื่อบริหารความเสี่ยงเสมอนะครับ "
        "หากต้องการให้ผมวิเคราะห์ส่วนไหนเพิ่มเติม ถามผมได้เลยครับ!"
    )

    answer_text = f"{greeting}\n\n{body_points}\n\n{takeaway}"
    return answer_text, []
