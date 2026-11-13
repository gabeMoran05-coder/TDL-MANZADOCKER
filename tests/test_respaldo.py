"""Pruebas del respaldo verificable de Bronce (src/respaldo.py)."""

from __future__ import annotations

import json
import zipfile

import pytest

from src.respaldo import crear, inventario, main, probar, verificar


@pytest.fixture
def raiz(tmp_path):
    bronce = tmp_path / "data" / "bronce"
    (bronce / "asipona" / "pdf").mkdir(parents=True)
    (bronce / "asipona" / "em_mensual.csv").write_text("anio,mes\n2026,1\n", encoding="utf-8")
    (bronce / "asipona" / "pdf" / "EM-2026-10.pdf").write_bytes(b"%PDF-1.4 prueba")
    (bronce / ".gitkeep").write_text("", encoding="utf-8")
    return tmp_path


def test_inventario_ignora_gitkeep(raiz):
    archivos = inventario(raiz)
    assert set(archivos) == {"data/bronce/asipona/em_mensual.csv",
                             "data/bronce/asipona/pdf/EM-2026-10.pdf"}


def test_ciclo_crear_restaurar_comparar(raiz, tmp_path):
    zip_ruta = tmp_path / "r.zip"
    m = crear(raiz, zip_ruta)
    assert m["total_archivos"] == 2
    r = verificar(zip_ruta, raiz)
    assert r["ok"] and r["errores"] == [] and r["archivos_verificados"] == 2


def test_detecta_cambio_en_bronce_despues_del_respaldo(raiz, tmp_path):
    zip_ruta = tmp_path / "r.zip"
    crear(raiz, zip_ruta)
    (raiz / "data/bronce/asipona/em_mensual.csv").write_text("alterado\n", encoding="utf-8")
    (raiz / "data/bronce/asipona/pdf/EM-2026-10.pdf").unlink()
    r = verificar(zip_ruta, raiz)
    assert not r["ok"]
    assert any("cambio" in e for e in r["errores"])
    assert any("ya no existe" in e for e in r["errores"])


def test_detecta_respaldo_corrupto(raiz, tmp_path):
    zip_ruta = tmp_path / "r.zip"
    crear(raiz, zip_ruta)
    corrupto = tmp_path / "corrupto.zip"
    with zipfile.ZipFile(zip_ruta) as origen, zipfile.ZipFile(corrupto, "w") as destino:
        for nombre in origen.namelist():
            datos = origen.read(nombre)
            if nombre.endswith(".csv"):
                datos = b"otro contenido"
            if nombre.endswith(".pdf"):
                continue  # archivo perdido
            destino.writestr(nombre, datos)
    r = verificar(corrupto)
    assert not r["ok"] and not r["comparado_con_bronce_vivo"]
    assert any("hash restaurado" in e for e in r["errores"])
    assert any("falta en el respaldo" in e for e in r["errores"])


def test_bronce_vacio_falla(tmp_path):
    (tmp_path / "data" / "bronce").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        crear(tmp_path, tmp_path / "r.zip")


def test_probar_guarda_evidencia(raiz):
    r = probar(raiz)
    assert r["ok"]
    guardado = json.loads((raiz / "calidad/e1/respaldo_prueba.json").read_text(encoding="utf-8"))
    assert guardado["archivos_verificados"] == 2
    assert len(guardado["manifiesto_sha256"]) == 64


def test_cli(raiz, tmp_path, capsys):
    zip_ruta = tmp_path / "cli.zip"
    assert main(["crear", "--raiz", str(raiz), "--salida", str(zip_ruta)]) == 0
    assert main(["verificar", str(zip_ruta), "--raiz", str(raiz)]) == 0
    assert main(["probar", "--raiz", str(raiz)]) == 0
    (raiz / "data/bronce/asipona/em_mensual.csv").write_text("x\n", encoding="utf-8")
    assert main(["verificar", str(zip_ruta), "--raiz", str(raiz)]) == 1
    assert "Respaldo creado" in capsys.readouterr().out
