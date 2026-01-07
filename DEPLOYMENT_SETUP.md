# 🚀 Minimi Trading Bot - 실제 배포 및 운영 가이드

## ❓ 중요한 질문: GitHub에서 실행 가능한가?

### 답변: **아니요, GitHub에서는 실행할 수 없습니다.**

GitHub는 **코드 저장소**일 뿐이며, 실제 프로그램을 실행하려면 별도의 **서버 환경**이 필요합니다.

---

## 🖥️ 실행 가능한 환경 3가지

### 1️⃣ 로컬 컴퓨터 (개인 PC/노트북)
**장점:**
- ✅ 무료
- ✅ 완전한 통제권
- ✅ 설정 간편

**단점:**
- ❌ 컴퓨터를 24시간 켜둬야 함
- ❌ 전기세 발생
- ❌ 인터넷 연결 필수
- ❌ 외부에서 대시보드 접속 어려움

**권장 대상:** 테스트 및 모의 투자 단계

---

### 2️⃣ 클라우드 서버 (AWS, GCP, Azure, Vultr 등)
**장점:**
- ✅ 24/7 자동 운영
- ✅ 안정적인 인터넷
- ✅ 외부 접속 가능
- ✅ 자동 재시작 설정 가능

**단점:**
- ❌ 월 비용 발생 (월 $5~20)

**권장 대상:** 실전 투자 및 장기 운영

**추천 서비스:**
- **AWS EC2** (t2.micro 프리티어 1년 무료)
- **Google Cloud** ($300 크레딧 제공)
- **Vultr** (월 $5부터)
- **DigitalOcean** (월 $4부터)
- **Oracle Cloud** (Always Free Tier)

---

### 3️⃣ 24시간 가동 가능한 개인 서버
**장점:**
- ✅ 한번 설정하면 계속 실행
- ✅ 추가 비용 없음
- ✅ 완전한 통제권

**단점:**
- ❌ 초기 하드웨어 투자 필요
- ❌ 관리 필요

**권장 대상:** 고급 사용자, 장기 운영

**추천 하드웨어:**
- 라즈베리파이 4 (약 5만원)
- 저전력 미니PC

---

## 📋 배포 단계별 가이드

### 🔵 방법 1: 로컬 컴퓨터에서 실행 (테스트용)

#### Step 1: Python 설치
```bash
# Windows
https://www.python.org/downloads/
# Python 3.8 이상 설치

# Mac
brew install python3

# Linux
sudo apt update
sudo apt install python3 python3-pip
```

#### Step 2: 프로젝트 클론
```bash
# 원하는 폴더에서 실행
git clone https://github.com/lcmin16-prog/minimi.git
cd minimi
```

#### Step 3: 의존성 설치
```bash
pip install -r requirements.txt
```

#### Step 4: 환경 설정
```bash
# .env 파일 생성
cp .env.example .env

# 텍스트 에디터로 .env 편집
# Windows: notepad .env
# Mac/Linux: nano .env
```

**.env 설정 (모의 투자용):**
```env
TRADE_MODE=paper
TICKER=KRW-BTC
RSI_PERIOD=14
TRADE_AMOUNT_KRW=10000.0
STOP_LOSS_PCT=0.02
TAKE_PROFIT_PCT=0.01
PAPER_INITIAL_KRW=1000000.0
```

#### Step 5: 실행
```bash
# Windows
python main.py

# Mac/Linux
python3 main.py
```

#### Step 6: 대시보드 실행 (별도 터미널)
```bash
# Windows
python dashboard.py

# Mac/Linux
python3 dashboard.py
```

#### Step 7: 브라우저에서 접속
```
http://localhost:5000
```

---

### 🟢 방법 2: AWS EC2 클라우드 배포 (실전용)

#### 📌 AWS 무료 계정 생성
1. https://aws.amazon.com/ 접속
2. "무료로 시작하기" 클릭
3. 계정 생성 (신용카드 필요, 1년간 무료)

#### 📌 EC2 인스턴스 생성

##### Step 1: EC2 대시보드 접속
- AWS 콘솔 → EC2 → "인스턴스 시작"

##### Step 2: 인스턴스 설정
- **이름:** minimi-trading-bot
- **AMI:** Ubuntu Server 22.04 LTS (프리티어)
- **인스턴스 유형:** t2.micro (프리티어)
- **키 페어:** 새로 생성 (다운로드 후 보관)
- **보안 그룹:**
  - SSH (포트 22): 내 IP만 허용
  - 커스텀 TCP (포트 5000): 내 IP만 허용

##### Step 3: 인스턴스 시작
- "인스턴스 시작" 클릭
- 2~3분 대기

##### Step 4: 인스턴스 접속
```bash
# Mac/Linux
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-instance-ip

# Windows (PuTTY 사용)
# PuTTY 다운로드 및 키 변환 필요
```

##### Step 5: 서버 초기 설정
```bash
# 시스템 업데이트
sudo apt update
sudo apt upgrade -y

# Python 및 Git 설치
sudo apt install -y python3 python3-pip git

# 프로젝트 클론
git clone https://github.com/lcmin16-prog/minimi.git
cd minimi

# 의존성 설치
pip3 install -r requirements.txt
```

##### Step 6: 환경 설정
```bash
# .env 파일 생성
cp .env.example .env
nano .env
```

**실전용 .env 설정:**
```env
TRADE_MODE=real  # 실전 모드
TICKER=KRW-BTC
RSI_PERIOD=14
TRADE_AMOUNT_KRW=10000.0
STOP_LOSS_PCT=0.02
TAKE_PROFIT_PCT=0.01

# 업비트 API 키 (필수!)
UPBIT_ACCESS_KEY=your_access_key_here
UPBIT_SECRET_KEY=your_secret_key_here
```

##### Step 7: Systemd 서비스 생성 (자동 시작)

**트레이딩 봇 서비스:**
```bash
sudo nano /etc/systemd/system/minimi-bot.service
```

**내용:**
```ini
[Unit]
Description=Minimi Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/minimi
ExecStart=/usr/bin/python3 /home/ubuntu/minimi/scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**대시보드 서비스:**
```bash
sudo nano /etc/systemd/system/minimi-dashboard.service
```

**내용:**
```ini
[Unit]
Description=Minimi Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/minimi
ExecStart=/usr/bin/python3 /home/ubuntu/minimi/dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

##### Step 8: 서비스 시작
```bash
# 서비스 활성화
sudo systemctl enable minimi-bot
sudo systemctl enable minimi-dashboard

# 서비스 시작
sudo systemctl start minimi-bot
sudo systemctl start minimi-dashboard

# 상태 확인
sudo systemctl status minimi-bot
sudo systemctl status minimi-dashboard
```

##### Step 9: 대시보드 접속
```
http://your-instance-ip:5000
```

##### Step 10: 로그 모니터링
```bash
# 봇 로그
tail -f /home/ubuntu/minimi/trades.log

# 대시보드 로그
sudo journalctl -u minimi-dashboard -f

# 시스템 로그
sudo journalctl -u minimi-bot -f
```

---

### 🟣 방법 3: 라즈베리파이 배포 (저렴한 24시간 서버)

#### 📌 필요한 것
- 라즈베리파이 4 (2GB 이상 권장)
- MicroSD 카드 (16GB 이상)
- 전원 어댑터
- 인터넷 연결 (이더넷 또는 Wi-Fi)

#### Step 1: 라즈베리파이 OS 설치
1. Raspberry Pi Imager 다운로드
2. Raspberry Pi OS Lite (64-bit) 선택
3. SD 카드에 설치
4. SSH 활성화

#### Step 2: SSH 접속
```bash
ssh pi@raspberrypi.local
# 기본 비밀번호: raspberry
```

#### Step 3: 프로젝트 설치 (AWS와 동일)
```bash
# 시스템 업데이트
sudo apt update
sudo apt upgrade -y

# Python 및 Git 설치
sudo apt install -y python3 python3-pip git

# 프로젝트 클론
git clone https://github.com/lcmin16-prog/minimi.git
cd minimi

# 의존성 설치
pip3 install -r requirements.txt

# .env 설정
cp .env.example .env
nano .env
```

#### Step 4: 자동 시작 설정
```bash
# crontab 편집
crontab -e

# 다음 줄 추가 (재부팅 시 자동 시작)
@reboot cd /home/pi/minimi && python3 scheduler.py > /home/pi/minimi/bot.log 2>&1 &
@reboot cd /home/pi/minimi && python3 dashboard.py > /home/pi/minimi/dashboard.log 2>&1 &
```

#### Step 5: 재부팅 및 확인
```bash
sudo reboot

# 재접속 후
ps aux | grep python
tail -f minimi/bot.log
```

---

## 🔐 보안 설정 (중요!)

### 1️⃣ .env 파일 보호
```bash
# 파일 권한 설정 (본인만 읽기 가능)
chmod 600 .env

# Git에서 제외 (.gitignore에 추가됨)
# .env 파일은 절대 커밋하지 마세요!
```

### 2️⃣ API 키 관리
- ✅ 절대 GitHub에 업로드하지 마세요
- ✅ API 키는 로컬/서버의 .env 파일에만 저장
- ✅ 정기적으로 API 키 교체
- ✅ IP 화이트리스트 설정 (업비트)

### 3️⃣ 서버 방화벽
```bash
# Ubuntu/Debian
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 5000  # Dashboard (필요시)
```

### 4️⃣ SSH 키 기반 인증
```bash
# 비밀번호 로그인 비활성화
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
sudo systemctl restart sshd
```

---

## 📊 운영 모니터링

### 1️⃣ 일일 체크리스트
```bash
# 봇 프로세스 확인
ps aux | grep python

# 로그 확인
tail -100 trades.log

# 시스템 리소스
top
df -h  # 디스크 용량
free -h  # 메모리
```

### 2️⃣ 성과 리포트
```bash
# 매일 실행
python report.py

# 결과 확인
cat trades.csv | tail -20
```

### 3️⃣ 대시보드 확인
- 브라우저에서 `http://your-server-ip:5000` 접속
- 총 자산, 수익률, 승률 확인

### 4️⃣ 자동 알림 설정 (선택사항)
- Telegram Bot 연동
- 이메일 알림
- SMS 알림

---

## 💰 비용 비교

| 방법 | 초기 비용 | 월 비용 | 전기세 | 총 1년 비용 |
|------|----------|---------|--------|------------|
| 로컬 PC | 0원 | 0원 | ~5,000원 | ~60,000원 |
| AWS EC2 (프리티어) | 0원 | 0원 (1년) | 0원 | 0원 (1년) |
| AWS EC2 (유료) | 0원 | $5 (6,500원) | 0원 | ~78,000원 |
| 라즈베리파이 | ~50,000원 | 0원 | ~500원 | ~56,000원 |
| VPS (Vultr) | 0원 | $5 (6,500원) | 0원 | ~78,000원 |

**추천:**
1. **테스트 단계:** 로컬 PC (무료)
2. **첫 1년:** AWS EC2 프리티어 (무료)
3. **장기 운영:** 라즈베리파이 (전기세만 발생)

---

## 🚨 트러블슈팅

### 문제 1: 프로세스가 멈춤
```bash
# 프로세스 재시작
pkill -f python
cd /home/user/minimi
python3 scheduler.py &
python3 dashboard.py &
```

### 문제 2: API 에러
```bash
# API 연결 테스트
python3 test_upbit_api.py

# .env 확인
cat .env | grep UPBIT
```

### 문제 3: 메모리 부족
```bash
# 메모리 확인
free -h

# 스왑 메모리 추가 (Linux)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 문제 4: 대시보드 접속 안 됨
```bash
# 방화벽 확인
sudo ufw status

# 포트 열기
sudo ufw allow 5000

# 프로세스 확인
ps aux | grep dashboard
```

---

## 📚 추가 자료

### 클라우드 배포 튜토리얼
- [AWS EC2 시작하기](https://aws.amazon.com/ko/ec2/getting-started/)
- [Google Cloud 무료 크레딧](https://cloud.google.com/free)
- [DigitalOcean 튜토리얼](https://www.digitalocean.com/community/tutorials)

### Python 자동화
- [Systemd 서비스 가이드](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Cron 사용법](https://crontab.guru/)

### 보안
- [SSH 키 생성](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
- [UFW 방화벽](https://help.ubuntu.com/community/UFW)

---

## ✅ 배포 체크리스트

### 준비 단계
- [ ] Python 3.8+ 설치 확인
- [ ] Git 설치 확인
- [ ] 서버 또는 PC 준비
- [ ] 인터넷 연결 확인

### 설치 단계
- [ ] 저장소 클론 (`git clone`)
- [ ] 의존성 설치 (`pip install -r requirements.txt`)
- [ ] .env 파일 생성 및 설정
- [ ] 업비트 API 키 등록 (실전 모드)

### 실행 단계
- [ ] 봇 실행 테스트 (`python main.py`)
- [ ] 대시보드 실행 (`python dashboard.py`)
- [ ] 브라우저 접속 확인
- [ ] 자동 시작 설정 (systemd 또는 cron)

### 운영 단계
- [ ] 일일 로그 확인
- [ ] 주간 성과 리포트
- [ ] 월간 전략 검토
- [ ] 정기 백업

---

## 🎯 권장 배포 방법

### 초보자
**→ 로컬 PC로 시작**
- 무료, 간단
- 1주일 모의 투자 테스트
- 익숙해진 후 클라우드 전환

### 중급자
**→ AWS EC2 프리티어**
- 1년 무료
- 24/7 자동 운영
- 실전 투자 가능

### 고급자
**→ 라즈베리파이 또는 VPS**
- 장기 운영
- 저렴한 유지비
- 완전한 통제권

---

## 📞 도움이 필요하면?

### GitHub Issues
https://github.com/lcmin16-prog/minimi/issues

### 문서 참고
- QUICKSTART.md (빠른 시작)
- OPERATION_GUIDE.md (운영 매뉴얼)
- UPBIT_API_GUIDE.md (API 설정)

---

## 🎉 결론

**GitHub는 코드 저장소일 뿐입니다.**  
실제 봇을 실행하려면 **서버 환경**이 필요합니다!

**추천 단계:**
1. 로컬 PC에서 테스트 (1주일)
2. AWS 프리티어로 실전 검증 (1년)
3. 안정화 후 라즈베리파이 또는 VPS로 전환

**지금 바로 시작하세요!** 🚀

---

**작성일:** 2026-01-06  
**문서 버전:** 1.0
