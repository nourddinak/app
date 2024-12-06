import flet as ft
import requests
import re
import asyncio
from typing import Optional


async def get_ip() -> str:
    """Fetch your public IP address asynchronously."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        response.raise_for_status()
        return response.json().get('ip')
    except Exception as e:
        return f"[Error] {e}"


async def get_fraud_score(ip: str) -> Optional[int]:
    """Fetch fraud score of the IP address from Scamalytics asynchronously."""
    try:
        url = f"https://scamalytics.com/ip/{ip}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        match = re.search(r"Fraud Score:\s*(\d+)", response.text)
        return int(match.group(1)) if match else None
    except Exception as e:
        return f"[Error] {e}"


def categorize_risk(fraud_score) -> str:
    """Categorize the risk level based on the fraud score."""
    if isinstance(fraud_score, int):
        if fraud_score < 20:
            return "Low Risk"
        elif 20 <= fraud_score < 70:
            return "Medium Risk"
        else:
            return "High Risk"
    return "Unknown"


async def main(page: ft.Page):
    page.window_width = 360
    page.window_height = 640
    page.window_resizable = False
    page.title = "IP Fraud Checker"
    page.bgcolor = "#2A323B"
    page.padding = 16
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.DARK
    page.fonts = {
        "RobotoSlab": "https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/RobotoSlab%5Bwght%5D.ttf"
    }

    # Loading animation
    loading_ring = ft.ProgressRing(
        width=16, 
        height=16, 
        stroke_width=2,
        visible=False
    )

    # Logo
    logo = ft.Image(
        src="assets/logo.png",
        width=100,
        height=100,
        fit=ft.ImageFit.CONTAIN,
    )

    # Create progress bar
    progress = ft.ProgressBar(visible=False)

    title = ft.Text(
        "IP Fraud Checker",
        size=24,
        font_family="RobotoSlab",
        weight=ft.FontWeight.BOLD,
        color="#FFFFFF"
    )

    ip_label = ft.Text(
        "Click to Fetch Your IP Address",
        size=16,
        color="#FFFFFF"
    )

    result_label = ft.Text(
        "",
        size=18,
        color="#FFFFFF"
    )

    def update_result_color(risk_level: str):
        if risk_level == "Low Risk":
            result_label.color = "green"
        elif risk_level == "Medium Risk":
            result_label.color = "yellow"
        elif risk_level == "High Risk":
            result_label.color = "red"
        else:
            result_label.color = "#FFFFFFB3"
        page.update()

    async def check_fraud_score(e):
        try:
            # Show loading
            loading_ring.visible = True
            progress.visible = True
            check_button.disabled = True
            result_label.color = "#FFFFFFB3"
            result_label.value = "Fetching data..."
            page.update()

            # Get IP
            ip = await get_ip()
            if "Error" in str(ip):
                ip_label.value = str(ip)
                result_label.value = "Failed to fetch fraud score."
                return

            ip_label.value = f"Your IP: {ip}"
            fraud_score = await get_fraud_score(ip)

            if isinstance(fraud_score, int):
                risk_level = categorize_risk(fraud_score)
                result_label.value = f"Fraud Score: {fraud_score}\nRisk Level: {risk_level}"
                update_result_color(risk_level)
            else:
                result_label.value = "Error fetching fraud score."

        except Exception as e:
            result_label.value = f"An error occurred: {str(e)}"
        finally:
            # Hide loading and enable button
            loading_ring.visible = False
            progress.visible = False
            check_button.disabled = False
            page.update()

    check_button = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Text("Check Fraud Score", size=16),
                    loading_ring
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color={
                    ft.MaterialState.DEFAULT: "#FFFFFF",
                },
                bgcolor={
                    ft.MaterialState.DEFAULT: "#218EF3",
                    ft.MaterialState.HOVERED: "#1A7AD1",
                    ft.MaterialState.DISABLED: "#CCCCCC",
                }
            ),
            width=200,
            height=48,
            on_click=check_fraud_score
        ),
        animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )

    # Card container
    card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    logo,
                    title,
                    progress,
                    ip_label,
                    result_label,
                    check_button
                ],
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=16,
        ),
        elevation=5,
        margin=10
    )

    page.add(card)

    # Add a subtle animation when the page loads
    await asyncio.sleep(0.1)
    card.opacity = 0
    await page.update_async()
    card.opacity = 1
    card.animate_opacity = ft.animation.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
    await page.update_async()


if __name__ == '__main__':
    try:
        ft.app(
            target=main,
            assets_dir="assets",
            view=ft.AppView.FLET_APP,
            port=8550
        )
    except Exception as e:
        print(f"Failed to start app: {e}")