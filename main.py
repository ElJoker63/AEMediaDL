import flet as ft
import yt_dlp
import os
import humanize
import asyncio
from time import localtime

seg = 0

ruta = "/storage/emulated/0/AEMedia"


def main(page: ft.Page):
    page.title = "AEMedia"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.auto_scroll = True
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.HIDDEN
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(primary="indigo", secondary="white"),
    )

    # Asegurarse de que el directorio de descargas existe
    if not os.path.exists(ruta):
        os.makedirs(ruta)

    app_bar = ft.AppBar(
        leading=ft.Icon(ft.Icons.SLOW_MOTION_VIDEO_ROUNDED),
        title=ft.Text("AEMedia"),
        center_title=True,
        bgcolor=ft.Colors.INDIGO,
    )

    downloads = ft.ListView(
        expand=True,
        spacing=0,
        padding=10,
        auto_scroll=False,
    )

    infodl = ft.ProgressBar(visible=False, color=ft.Colors.GREEN)

    def update_list():
        downloads.controls.clear()
        for file in os.listdir(ruta):
            ext = os.path.basename(file).split(".")[-1]
            if ext in ["mp4", "mkv", "mp3"]:
                icon = (
                    ft.Icons.VIDEO_FILE
                    if ext in ["mp4", "mkv"]
                    else ft.Icons.MUSIC_NOTE_ROUNDED
                )
            else:
                icon = ft.Icons.INSERT_DRIVE_FILE

            downloads.controls.append(
                ft.Card(
                    color=ft.Colors.INDIGO,
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    leading=ft.Icon(icon, size=50),
                                    title=ft.Text(f"{file}", no_wrap=True),
                                    subtitle=ft.Row(
                                        [
                                            ft.Text(
                                                f"{humanize.naturalsize(os.path.getsize(ruta + '/' +file))}"
                                            ),
                                            ft.IconButton(
                                                ft.Icons.DELETE, icon_color="red", on_click=lambda _, f=file: delete_file(f)
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.END,
                                    ),
                                ),
                            ]
                        ),
                        padding=0,
                    ),
                )
            )
        page.update()

    def alert(code, msg):
        Colors = {
            "info": ('BLUE', ft.Colors.WHITE),
            "ok": ('GREEN', ft.Colors.WHITE),
            "alert": ('YELLOW', ft.Colors.BLACK),
            "error": ('RED', ft.Colors.WHITE),
            "ok.ru": ('ORANGE', ft.Colors.WHITE),            
            "insta": ('PURPLE', ft.Colors.WHITE),
        }
        color, ftcolor = Colors.get(code, (ft.Colors.GREY, ft.Colors.BLACK))
        return ft.SnackBar(content=ft.Text(msg, color=ftcolor), duration=1500, bgcolor=color)

    def download_progress(data):
        if data["status"] == "downloading":
            filename = data["filename"].split("/")[-1]
            _downloaded_bytes_str = data["_downloaded_bytes_str"]
            _total_bytes_str = data["_total_bytes_str"]
            if _total_bytes_str == "N/A":
                _total_bytes_str = data["_total_bytes_estimate_str"]
            _speed_str = data["_speed_str"].replace(" ", "")
            _eta_str = data["_eta_str"]
            progress_value = data['downloaded_bytes'] / data['total_bytes'] if data['total_bytes'] else 0
            global seg
            if seg != localtime().tm_sec:
                infodl.visible = True
                infodl.value = progress_value
                update_list()
                page.update()
            seg = localtime().tm_sec

    async def ytdlp_downloader(url, callback):
        class YT_DLP_LOGGER(object):
            def debug(self, msg):
                pass

            def warning(self, msg):
                pass

            def error(self, msg):
                pass

        dlp_opts = {
            "logger": YT_DLP_LOGGER(),
            "progress_hooks": [callback],
            "outtmpl": "/storage/emulated/0/AEMedia/%(title)s.%(ext)s",
            "format": "best[height<=720]/best[height<=480]/best",  # Si no encuentra 480p, usará la mejor calidad disponible
            "extract_flat": False,
            "no_warnings": True,
            "quiet": True,
        }

        try:
            downloader = yt_dlp.YoutubeDL(dlp_opts)
            filedata = await asyncio.get_running_loop().run_in_executor(
                None, downloader.extract_info, url
            )
            return downloader.prepare_filename(filedata)
        except Exception as e:
            page.open(alert("error", f"Error al descargar: {str(e)}"))
            page.update()

    async def download_video(url):
        try:
            await ytdlp_downloader(url, download_progress)
            update_list()
            infodl.visible = False
            page.update()
            page.open(alert("ok", "DESCARGA COMPLETADA"))
            page.update()
        except Exception as e:
            print(str(e))
            page.open(alert("error", str(e)))
            page.update()
        infodl.controls.clear()
        infodl.update()

    async def get_name(url):
        if 'xnxx' in url:
            page.open(alert("info", "DESCARGANDO DE XNXX"))
            page.update()
        if 'youtube' in url:
            page.open(alert("error", "DESCARGANDO DE YOUTUBE"))
            page.update()
        if 'ok.ru' in url:
            page.open(alert("ok.ru", "DESCARGANDO DE OK.RU"))
            page.update()
        if 'pinterest' in url:
            page.open(alert("error", "DESCARGANDO DE PINTEREST"))
            page.update()
        if 'insta' in url:
            page.open(alert("insta", "DESCARGANDO DE INSTAGRAM"))
            page.update()
        else:
            page.open(alert("info", "DESCARGANDO"))
            page.update()
        try:
            await download_video(url)
        except Exception as e:
            print(str(e))
            page.open(alert("error", str(e)))
            page.update()
        update_list()

    def delete_file(file):
        try:
            os.unlink(f"{ruta}/{file}")
            page.open(alert("ok", f"ARCHIVO {file} ELIMINADO"))
            page.update()
            update_list()
        except:
            page.open(alert("error", "OCURRIO UN ERROR"))
            page.update()
            update_list()
        page.update()

    info = ft.Row(
        controls=[ft.Text("App para descargas de Instagram, Pinterest, Xnxx, Youtube y Ok.ru", size=14)], alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=30
    )
    url = ft.TextField(label="URL", border_color="indigo", border_radius=35, on_submit=lambda _: asyncio.run(get_name(url.value)))
    button = ft.Row(
        [
            ft.TextButton(
                content=ft.Row(
                    [
                        ft.Image(
                            src=f"/icon.png",
                            height=30,
                            width=30,
                            color=ft.Colors.INDIGO,
                        ),
                        ft.Text("DESCARGAR", font_family="Qs-B", size=20, color=ft.Colors.INDIGO),
                    ]
                ),
                on_click=lambda _: asyncio.run(get_name(url.value)),
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    update_list()

    page.add(
        app_bar,
        #info,
        infodl,
        ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
        url,
        button,
        downloads,
    )

ft.app(target=main, assets_dir='assets')