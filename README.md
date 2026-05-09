# TikTok Affiliate AI Auto Content Machine 🚀

ระบบออโตเมชั่นสำหรับนักทำการตลาด Affiliate (นายหน้า) แบบครบวงจรและพร้อมใช้งานบนระดับโปรดักชั่น ระบบนี้ถูกออกแบบมาเป็น **Growth & Profit Optimization Engine** ที่จะช่วยคุณหาเทรนด์สินค้า, สร้างเนื้อหาด้วย AI แบบ A/B Testing, ออโต้โพสต์, และปรับกลยุทธ์ตามรายได้ (Revenue) ที่เกิดขึ้นจริง

## 🏗 ภาพรวมของระบบ (System Architecture)

ระบบถูกออกแบบให้ทำงานแบบ Asynchronous ผ่าน Celery Worker โดยแยกการทำงานของ Frontend (Vite/React) และ Backend (FastAPI) ออกจากกัน

### Architecture Flow Diagram
```text
[Frontend (React/Vite)] <---> [Backend (FastAPI)] <---> [PostgreSQL]
                                       |
                                       v
                             [Redis (Message Broker)]
                                       |
             +---------------------------------------------------+
             |                  Celery Workers                   |
             |                                                   |
             |  1. Scraper / Trend Discovery                     |
             |      (Creative Center -> API -> Scraper)          |
             |                                                   |
             |  2. AI Content Generator (Google Gemini/OpenAI)   |
             |      (Hooks, Captions, Voice/Video Scripts)       |
             |                                                   |
             |  3. Multi-Account Poster & Queue Manager          |
             |      (Checks Trust Score & Shadowbans)            |
             +---------------------------------------------------+
```

### ฟีเจอร์หลัก
1. **ระบบดึงข้อมูลเทรนด์ (TikTok Trend Discovery)**: ดึงข้อมูลเทรนด์แบบ Hybrid (Creative Center -> API -> Scraper -> Mock) มีระบบป้องกันการแบนด้วยการสลับ User-Agents
2. **ระบบคิดคะแนนอัจฉริยะ (Smart Decision Engine)**: คำนวณคะแนนเทรนด์ (`trend_score`) จากยอดไลก์และยอดวิว
   - **Score >= 80**: สินค้ามาแรงสุดๆ AI จะสร้างเนื้อหาและโพสต์ทันทีโดยไม่ต้องรออนุมัติ
   - **Score >= 50 และ < 80**: สินค้าระดับกลาง ระบบจะสร้างเนื้อหาไว้และรอให้คุณกดตรวจสอบ (Review)
3. **ระบบสุ่มและเรียนรู้ของ AI (Exploration vs Exploitation 80/20)**: สร้างคอนเทนต์หลายรูปแบบ และสอดแทรก **Learning Memory Decay** เพื่อให้ AI ให้น้ำหนักกับรูปแบบโพสต์ที่ไวรัลในอดีต "ล่าสุด" ก่อนเสมอ
4. **Short Video Pipeline Scaffold**: AI ไม่ได้สร้างแค่ข้อความ แต่ถูกปรับคำสั่ง (Prompts) ให้เตรียมข้อมูลเป็น สคริปต์เสียง (Voice Script), คำบรรยาย (Subtitle), และแนะนำภาพ (Scene Suggestions) ไว้สำหรับต่อยอดการทำวิดีโอแบบออโต้ในอนาคต
5. **ระบบความน่าเชื่อถือและการกระจายความเสี่ยง (Account Trust & Risk Control)**: ระบบประเมิน **Trust Score** ให้กับทุกบัญชีโซเชียลมีเดีย หากพบว่าบัญชีมีโอกาสถูกระงับการมองเห็น (Shadowbanned) คะแนน Trust Score จะลดลง และระบบจะโอนคิวโพสต์ไปยังบัญชีอื่นที่ปลอดภัยกว่าทันที

## 🛠 สิ่งที่ต้องมีก่อนเริ่มใช้งาน (Prerequisites)

- Docker & Docker Compose
- (แนะนำ) OpenAI API Key เพื่อใช้งาน AI ในการคิดคอนเทนต์แบบสมจริง (ถ้าไม่มี ระบบจะมี Mock เพื่อจำลองการทำงานให้)

## 🚀 วิธีการติดตั้งและเริ่มใช้งาน

### 1. ตั้งค่า Environment

คัดลอกไฟล์ `.env.example` ไปเป็น `.env`:
```bash
cp .env.example .env
```
แก้ไขไฟล์ `.env` และใส่ค่า `OPENAI_API_KEY` ของคุณลงไป

### 2. รันระบบทั้งหมด

ใช้คำสั่งด้านล่างนี้ ระบบจะทำการเปิด Database, Redis, FastAPI Backend, Celery Worker, และ React Frontend ขึ้นมาผ่าน Docker:

```bash
./run.sh
```
*หรือสามารถรันด้วยคำสั่ง `docker-compose up --build -d` ก็ได้เช่นกัน*

### 3. เตรียมฐานข้อมูล (Database Migrations)

หลังจากที่คอนเทนเนอร์ทำงาน ให้เรารันคำสั่งสร้างตารางในฐานข้อมูล:
```bash
docker-compose exec backend alembic upgrade head
```

### 4. วิธีเข้าใช้งาน

- **หน้าแอดมิน (Frontend Dashboard)**: [http://localhost:5173](http://localhost:5173)
- **เอกสาร API (Backend Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📖 คู่มือการใช้งานแบบละเอียด
โปรดอ่านรายละเอียดเชิงลึกและวิธีใช้งานแดชบอร์ดที่ไฟล์ [MANUAL_TH.md](MANUAL_TH.md)
