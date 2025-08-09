#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def full_page_check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 콘솔 메시지 수집
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        await page.goto("http://localhost:5173")
        await page.wait_for_timeout(3000)

        # 스크린샷
        await page.screenshot(path="/tmp/full_page_check.png", full_page=True)

        # 페이지 전체 분석
        analysis = await page.evaluate("""
            () => {
                // 페이지 제목
                const title = document.title;

                // 모든 버튼 찾기
                const buttons = document.querySelectorAll('button');
                const inputs = document.querySelectorAll('input');

                // 첫 번째 버튼의 스타일
                const firstButton = buttons[0];
                const buttonStyle = firstButton ? window.getComputedStyle(firstButton) : null;

                // <style> 태그 찾기
                const styleTag = document.querySelector('style[data-vite-dev-id*="index.css"]');

                return {
                    title,
                    buttonCount: buttons.length,
                    inputCount: inputs.length,
                    hasStyleTag: !!styleTag,
                    styleTagContent: styleTag ? styleTag.textContent.substring(0, 200) : null,
                    firstButtonStyle: buttonStyle ? {
                        backgroundColor: buttonStyle.backgroundColor,
                        color: buttonStyle.color,
                        borderRadius: buttonStyle.borderRadius,
                        padding: buttonStyle.padding,
                        fontSize: buttonStyle.fontSize
                    } : null,
                    bodyStyle: {
                        backgroundColor: window.getComputedStyle(document.body).backgroundColor,
                        fontFamily: window.getComputedStyle(document.body).fontFamily
                    }
                };
            }
        """)

        print("=== 페이지 전체 분석 ===")
        print(f"페이지 제목: {analysis['title']}")
        print(f"버튼 개수: {analysis['buttonCount']}")
        print(f"입력 필드 개수: {analysis['inputCount']}")
        print(f"스타일 태그 존재: {analysis['hasStyleTag']}")

        if analysis['styleTagContent']:
            print(f"\n스타일 태그 내용 (처음 200자):")
            print(analysis['styleTagContent'])

        if analysis['firstButtonStyle']:
            print(f"\n첫 번째 버튼 스타일:")
            for key, value in analysis['firstButtonStyle'].items():
                print(f"  {key}: {value}")

        print(f"\nBody 스타일:")
        for key, value in analysis['bodyStyle'].items():
            print(f"  {key}: {value}")

        if console_messages:
            print(f"\n콘솔 메시지 ({len(console_messages)}개):")
            for msg in console_messages[:5]:  # 처음 5개만
                print(f"  {msg}")

        print(f"\n스크린샷: /tmp/full_page_check.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(full_page_check())
