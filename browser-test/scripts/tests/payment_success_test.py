#!/usr/bin/env python3
"""
Payment Success Test - 支付成功场景自动化测试
包含: JWT生成 -> 创建订单 -> 浏览器自动化测试
"""

import jwt
import uuid
import time
import string
import random
import json
import os
import sys
from datetime import datetime

import requests as http_requests
from playwright.sync_api import sync_playwright

# ── 配置 ──
SCREENSHOT_DIR = "/Users/shmiwangzecheng/.claude/skills/browser-test/scripts/screenshots"
TIMESTAMP_TAG = datetime.now().strftime("%Y%m%d_%H%M%S")
TIMEOUT_SINGLE = 30_000   # 30s 单操作超时
TIMEOUT_OVERALL = 120_000 # 120s 整体超时

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def screenshot_path(name: str) -> str:
    return os.path.join(SCREENSHOT_DIR, f"{name}_{TIMESTAMP_TAG}.png")


def take_screenshot(page, step_name):
    filepath = screenshot_path(step_name)
    page.screenshot(path=filepath, full_page=True)
    return filepath


# ═══════════════════════════════════════════
# 步骤 1: 生成 JWT Token
# ═══════════════════════════════════════════
print("=" * 60)
print("步骤 1: 生成 JWT Token")
print("=" * 60)

date_str = datetime.now().strftime("%Y%m%d")
rand_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
user_uid = f"{date_str}_{rand_chars}"
print(f"  userUid: {user_uid}")

now_sec = int(time.time())

# 直接平铺 TokenPayload 字段（严格按用户原始要求）
payload = {
    "userUid": user_uid,
    "nickname": "Test User",
    "avatar": "https://lh3.googleusercontent.com/a/ACg8ocJeoCb98S8JAh_2bJez9iL_Hc9FYyzHyVAK0sSF6n6d9HUMJPwu=s96-c",
    "source": "web",
    "clientIp": "210.57.99.100",
    "tokenVer": "N-20251216",
    "loginAccountId": 687,
    "identityType": 2,
    "jti": str(uuid.uuid4()),
    "iat": now_sec,
    "exp": now_sec + 300000,
}

# 打印 token 的 payload 调试信息
print(f"  payload (debug): {json.dumps(payload, ensure_ascii=False)}")

SECRET = "employment_leon123"
token = jwt.encode(payload, SECRET, algorithm="HS256")
print(f"  Token 生成状态: 成功")
print(f"  Token (前80字符): {token[:80]}...")

# ═══════════════════════════════════════════
# 步骤 2: 调用创建订单接口
# ═══════════════════════════════════════════
print()
print("=" * 60)
print("步骤 2: 调用创建订单接口")
print("=" * 60)

api_url = "http://test-zp.palmplaystore.com/job/order/prepay"
headers = {
    "apiVersion": "100004",
    "token": token,
    "Content-Type": "application/json",
}
body = {
    "productId": "goods_dnvy-KHwQCuT5r4G5i96Og",
    "channel": "paynicorn",
    "jumpLink": "https://test.ezhiredbd.com/hire/premium-center/premium-list?channel=paynicorn&status=0",
}

resp = http_requests.post(api_url, headers=headers, json=body, timeout=30)
resp_json = resp.json()
print(f"  HTTP状态码: {resp.status_code}")
print(f"  响应code: {resp_json.get('code')}")
print(f"  响应msg: {resp_json.get('msg')}")

if resp_json.get("code") != 10000:
    print(f"  [错误] 接口返回非10000, 终止测试")
    print(f"  完整响应: {json.dumps(resp_json, ensure_ascii=False, indent=2)}")
    sys.exit(1)

data = resp_json.get("data", {})
web_url = data.get("webUrl", "")
order_id = data.get("orderId", "N/A")
print(f"  orderId: {order_id}")
print(f"  webUrl: {web_url}")

if not web_url:
    print("  [错误] webUrl 为空, 终止测试")
    sys.exit(1)

# ═══════════════════════════════════════════
# 步骤 3: 浏览器自动化测试
# ═══════════════════════════════════════════
print()
print("=" * 60)
print("步骤 3: 浏览器自动化测试")
print("=" * 60)

results = {
    "page_loaded": {"status": "未执行", "detail": ""},
    "click_payment": {"status": "未执行", "detail": ""},
    "url_redirect": {"status": "未执行", "detail": ""},
}
screenshots = []
final_url = ""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        ignore_https_errors=True,
    )
    page = context.new_page()
    page.set_default_timeout(TIMEOUT_SINGLE)

    try:
        # 3.1 打开 webUrl
        print(f"  [3.1] 打开 webUrl ...")
        page.goto(web_url, wait_until="domcontentloaded", timeout=TIMEOUT_SINGLE)
        ss1 = take_screenshot(page, "step1_page_loaded")
        screenshots.append(ss1)
        print(f"  截图: {ss1}")

        # 3.2 等待 div.tips 出现
        print(f"  [3.2] 等待 div.tips (Choose one to continue) ...")
        try:
            page.wait_for_selector("div.tips", timeout=TIMEOUT_SINGLE)
        except Exception:
            # 检查是否有 "Illegal operation" 弹窗
            print("  [3.2] 初次等待超时，检查是否有 Illegal operation 弹窗 ...")
            illegal_popup = page.query_selector("text=Illegal operation")
            if illegal_popup:
                print("  [3.2] 发现 Illegal operation 弹窗，尝试关闭 ...")
                confirm_btn = (
                    page.query_selector("button:has-text('OK')")
                    or page.query_selector("button:has-text('Confirm')")
                    or page.query_selector("button:has-text('确定')")
                    or page.query_selector(".btn-confirm")
                    or page.query_selector(".dialog button")
                )
                if confirm_btn:
                    confirm_btn.click()
                    print("  [3.2] 已点击确认按钮")
                    time.sleep(1)
                page.wait_for_selector("div.tips", timeout=TIMEOUT_SINGLE)
            else:
                raise

        tips_el = page.query_selector("div.tips")
        tips_text = tips_el.inner_text() if tips_el else ""
        print(f"  tips 内容: {tips_text}")

        ss2 = take_screenshot(page, "step2_tips_visible")
        screenshots.append(ss2)
        print(f"  截图: {ss2}")

        if "Choose one to continue" in tips_text:
            results["page_loaded"] = {"status": "通过", "detail": tips_text}
        else:
            results["page_loaded"] = {"status": "失败", "detail": f"tips内容不匹配: {tips_text}"}

        # 3.3 点击 Payment Succeeded
        print(f"  [3.3] 点击 'Payment Succeeded' ...")
        payment_el = page.wait_for_selector(
            "span.status:has-text('Payment Succeeded')", timeout=TIMEOUT_SINGLE
        )
        if payment_el:
            payment_el.click()
            results["click_payment"] = {"status": "通过", "detail": "已点击 Payment Succeeded"}
            print("  已点击 Payment Succeeded")
        else:
            results["click_payment"] = {"status": "失败", "detail": "未找到元素"}

        time.sleep(2)
        ss3 = take_screenshot(page, "step3_clicked")
        screenshots.append(ss3)
        print(f"  截图: {ss3}")

        # 3.4 等待导航完成
        print(f"  [3.4] 等待页面导航完成 ...")
        try:
            page.wait_for_url("**/hire/login**", timeout=TIMEOUT_SINGLE)
        except Exception:
            print("  wait_for_url 超时，尝试 networkidle ...")
            try:
                page.wait_for_load_state("networkidle", timeout=10_000)
            except Exception:
                pass

        time.sleep(2)
        final_url = page.url
        print(f"  最终 URL: {final_url}")

        ss4 = take_screenshot(page, "step3_final_url")
        screenshots.append(ss4)
        print(f"  截图: {ss4}")

        if "test.ezhiredbd.com/hire/login" in final_url:
            results["url_redirect"] = {"status": "通过", "detail": final_url}
        else:
            results["url_redirect"] = {"status": "失败", "detail": f"实际URL: {final_url}"}

    except Exception as e:
        print(f"  [异常] {type(e).__name__}: {e}")
        try:
            ss_err = take_screenshot(page, "error")
            screenshots.append(ss_err)
        except Exception:
            pass
    finally:
        browser.close()

# ═══════════════════════════════════════════
# 汇总输出
# ═══════════════════════════════════════════
print()
print("=" * 60)
print("测试完成")
print("=" * 60)
print(f"  userUid       : {user_uid}")
print(f"  orderId       : {order_id}")
print(f"  webUrl        : {web_url}")
print(f"  最终URL       : {final_url}")
print(f"  页面加载      : {results['page_loaded']['status']} - {results['page_loaded']['detail']}")
print(f"  点击支付成功  : {results['click_payment']['status']} - {results['click_payment']['detail']}")
print(f"  URL跳转       : {results['url_redirect']['status']} - {results['url_redirect']['detail']}")
print(f"  截图文件数    : {len(screenshots)}")
for s in screenshots:
    print(f"    - {s}")

passed = sum(1 for r in results.values() if r["status"] == "通过")
total = len(results)
print(f"\n  通过: {passed}/{total} | 失败: {total - passed}/{total}")

# 输出 JSON 供外部解析
output = {
    "userUid": user_uid,
    "orderId": order_id,
    "webUrl": web_url,
    "finalUrl": final_url,
    "results": results,
    "screenshots": screenshots,
    "passed": passed,
    "total": total,
}
print("\n===TEST_RESULTS_JSON===")
print(json.dumps(output, ensure_ascii=False, indent=2))
print("===END_TEST_RESULTS===")
