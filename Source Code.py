"""
AI PC Builder System - Complete Integrated Application
Run this file directly to start both the API server and menu interface
"""

import json
import threading
import time
import requests

from fastapi import FastAPI
from fastapi.responses import JSONResponse

import uvicorn
from contextlib import asynccontextmanager

try:
    from langchain_ollama import OllamaLLM
    LANGCHAIN_AVAILABLE = True
except Exception:
    LANGCHAIN_AVAILABLE = False

# ==================== DATA (Embedded JSON) ====================

BUILD_CACHE = {}

PRODUCTS_DATA = {
  "cpu": [
    {
      "name": "AMD Ryzen 3 4100",
      "brand": "AMD",
      "series": "Ryzen 3",
      "model": "4100",
      "socket": "AM4",
      "memoryType": "DDR4",
      "estimatedPriceMYR": 249
    },
    {
      "name": "AMD Ryzen 5 5600G",
      "brand": "AMD",
      "series": "Ryzen 5",
      "model": "5600G",
      "socket": "AM4",
      "memoryType": "DDR4",
      "estimatedPriceMYR": 489
    },
    {
      "name": "AMD Ryzen 5 5600X",
      "brand": "AMD",
      "series": "Ryzen 5",
      "model": "5600X",
      "socket": "AM4",
      "memoryType": "DDR4",
      "estimatedPriceMYR": 649
    },
    {
      "name": "AMD Ryzen 7 5800X3D",
      "brand": "AMD",
      "series": "Ryzen 7",
      "model": "5800X3D",
      "socket": "AM4",
      "memoryType": "DDR4",
      "estimatedPriceMYR": 1399
    },
    {
      "name": "AMD Ryzen 9 5950X",
      "brand": "AMD",
      "series": "Ryzen 9",
      "model": "5950X",
      "socket": "AM4",
      "memoryType": "DDR4",
      "estimatedPriceMYR": 1999
    },
    {
      "name": "AMD Ryzen 5 7600",
      "brand": "AMD",
      "series": "Ryzen 5",
      "model": "7600",
      "socket": "AM5",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 599
    },
    {
      "name": "AMD Ryzen 5 8600G",
      "brand": "AMD",
      "series": "Ryzen 5",
      "model": "8600G",
      "socket": "AM5",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 699
    },
    {
      "name": "AMD Ryzen 7 7700X",
      "brand": "AMD",
      "series": "Ryzen 7",
      "model": "7700X",
      "socket": "AM5",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 999
    },
    {
      "name": "AMD Ryzen 7 8700G",
      "brand": "AMD",
      "series": "Ryzen 7",
      "model": "8700G",
      "socket": "AM5",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 1399
    },
    {
      "name": "AMD Ryzen 9 7950X",
      "brand": "AMD",
      "series": "Ryzen 9",
      "model": "7950X",
      "socket": "AM5",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 2299
    },
    {
      "name": "AMD Ryzen 9 9950X",
      "brand": "AMD",
      "series": "Ryzen 9000 Series",
      "model": "9950X",
      "socket": "AM5",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 3499
    },
    {
      "name": "Intel Core i3-10100F",
      "brand": "Intel",
      "series": "Core i3",
      "model": "10100F",
      "socket": "LGA1200",
      "memoryType": "DDR4",
      "estimatedPriceMYR": 299
    },
    {
      "name": "Intel Core i5-11400F",
      "brand": "Intel",
      "series": "Core i5",
      "model": "11400F",
      "socket": "LGA1200",
      "memoryType": "DDR4",
      "estimatedPriceMYR": 499
    },
    {
      "name": "Intel Core i5-11600K",
      "brand": "Intel",
      "series": "Core i5",
      "model": "11600K",
      "socket": "LGA1200",
      "memoryType": "DDR4",
      "estimatedPriceMYR": 599
    },
    {
      "name": "Intel Core i7-11700K",
      "brand": "Intel",
      "series": "Core i7",
      "model": "11700K",
      "socket": "LGA1200",
      "memoryType": "DDR4",
      "estimatedPriceMYR": 1199
    },
    {
      "name": "Intel Core i9-11900K",
      "brand": "Intel",
      "series": "Core i9",
      "model": "11900K",
      "socket": "LGA1200",
      "memoryType": "DDR4",
      "estimatedPriceMYR": 1599
    },
    {
      "name": "Intel Core i3-13100F",
      "brand": "Intel",
      "series": "Core i3",
      "model": "13100F",
      "socket": "LGA1700",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 359
    },
    {
      "name": "Intel Core i5-13400F",
      "brand": "Intel",
      "series": "Core i5",
      "model": "13400F",
      "socket": "LGA1700",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 699
    },
    {
      "name": "Intel Core i5-13600KF",
      "brand": "Intel",
      "series": "Core i5",
      "model": "13600KF",
      "socket": "LGA1700",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 899
    },
    {
      "name": "Intel Core i7-14700K",
      "brand": "Intel",
      "series": "Core i7",
      "model": "14700K",
      "socket": "LGA1700",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 2199
    },
    {
      "name": "Intel Core i9-14900K",
      "brand": "Intel",
      "series": "Core i9",
      "model": "14900K",
      "socket": "LGA1700",
      "memoryType": "DDR5",
      "estimatedPriceMYR": 2999
    }
  ],

  "motherboard": [
    {
      "name": "MSI A520M-A PRO",
      "brand": "MSI",
      "socket": "AM4",
      "memoryType": ["DDR4"],
      "formFactor": "Micro-ATX",
      "estimatedPriceMYR": 249
    },
    {
      "name": "ASUS TUF Gaming B550M-PLUS",
      "brand": "ASUS",
      "socket": "AM4",
      "memoryType": ["DDR4"],
      "formFactor": "Micro-ATX",
      "estimatedPriceMYR": 499
    },
    {
      "name": "Gigabyte B650M DS3H",
      "brand": "Gigabyte",
      "socket": "AM5",
      "memoryType": ["DDR5"],
      "formFactor": "Micro-ATX",
      "estimatedPriceMYR": 699
    },
    {
      "name": "MSI MAG B650 Tomahawk WiFi",
      "brand": "MSI",
      "socket": "AM5",
      "memoryType": ["DDR5"],
      "formFactor": "ATX",
      "estimatedPriceMYR": 1099
    },
    {
      "name": "MSI PRO B560M-A",
      "brand": "MSI",
      "socket": "LGA1200",
      "memoryType": ["DDR4"],
      "formFactor": "Micro-ATX",
      "estimatedPriceMYR": 349
    },
    {
      "name": "ASUS PRIME B560M-A",
      "brand": "ASUS",
      "socket": "LGA1200",
      "memoryType": ["DDR4"],
      "formFactor": "Micro-ATX",
      "estimatedPriceMYR": 449
    },
    {
      "name": "ASUS PRIME H610M-K",
      "brand": "ASUS",
      "socket": "LGA1700",
      "memoryType": ["DDR4"],
      "formFactor": "Micro-ATX",
      "estimatedPriceMYR": 359
    },
    {
      "name": "Gigabyte B760M DS3H AX",
      "brand": "Gigabyte",
      "socket": "LGA1700",
      "memoryType": ["DDR4", "DDR5"],
      "formFactor": "Micro-ATX",
      "estimatedPriceMYR": 699
    },
    {
      "name": "MSI Z790 Gaming Plus WiFi",
      "brand": "MSI",
      "socket": "LGA1700",
      "memoryType": ["DDR5"],
      "formFactor": "ATX",
      "estimatedPriceMYR": 1299
    }
  ],

  "gpu": [
    {
      "name": "NVIDIA GTX 1650",
      "brand": "NVIDIA",
      "vram": "4GB",
      "recommendedPSU": 450,
      "estimatedPriceMYR": 599,
      "useCase": ["office", "budget gaming"]
    },
    {
      "name": "AMD Radeon RX 6600",
      "brand": "AMD",
      "vram": "8GB",
      "recommendedPSU": 500,
      "estimatedPriceMYR": 1099,
      "useCase": ["gaming"]
    },
    {
      "name": "NVIDIA RTX 3060",
      "brand": "NVIDIA",
      "vram": "12GB",
      "recommendedPSU": 550,
      "estimatedPriceMYR": 1299,
      "useCase": ["gaming", "editing", "ai"]
    },
    {
      "name": "NVIDIA RTX 4060",
      "brand": "NVIDIA",
      "vram": "8GB",
      "recommendedPSU": 550,
      "estimatedPriceMYR": 1599,
      "useCase": ["gaming", "editing", "ai"]
    },
    {
      "name": "NVIDIA RTX 4060 Ti",
      "brand": "NVIDIA",
      "vram": "8GB",
      "recommendedPSU": 550,
      "estimatedPriceMYR": 1999,
      "useCase": ["gaming", "editing", "ai"]
    },
    {
      "name": "AMD Radeon RX 7800 XT",
      "brand": "AMD",
      "vram": "16GB",
      "recommendedPSU": 700,
      "estimatedPriceMYR": 2599,
      "useCase": ["gaming", "editing"]
    },
    {
      "name": "NVIDIA RTX 4070 SUPER",
      "brand": "NVIDIA",
      "vram": "12GB",
      "recommendedPSU": 650,
      "estimatedPriceMYR": 2999,
      "useCase": ["high-end gaming", "ai", "rendering"]
    }
  ],

  "ram": [
    {
      "name": "Kingston Fury Beast 8GB DDR4",
      "brand": "Kingston",
      "capacity": "8GB",
      "memoryType": "DDR4",
      "speed": "3200MHz",
      "estimatedPriceMYR": 99
    },
    {
      "name": "Kingston Fury Beast 16GB DDR4",
      "brand": "Kingston",
      "capacity": "16GB",
      "memoryType": "DDR4",
      "speed": "3200MHz",
      "estimatedPriceMYR": 179
    },
    {
      "name": "Corsair Vengeance LPX 32GB DDR4",
      "brand": "Corsair",
      "capacity": "32GB",
      "memoryType": "DDR4",
      "speed": "3600MHz",
      "estimatedPriceMYR": 349
    },
    {
      "name": "Kingston Fury Beast 8GB DDR5",
      "brand": "Kingston",
      "capacity": "8GB",
      "memoryType": "DDR5",
      "speed": "5200MHz",
      "estimatedPriceMYR": 149
    },
    {
      "name": "Kingston Fury Beast 16GB DDR5",
      "brand": "Kingston",
      "capacity": "16GB",
      "memoryType": "DDR5",
      "speed": "5600MHz",
      "estimatedPriceMYR": 299
    },
    {
      "name": "Corsair Dominator Platinum 32GB DDR5",
      "brand": "Corsair",
      "capacity": "32GB",
      "memoryType": "DDR5",
      "speed": "6000MHz",
      "estimatedPriceMYR": 699
    }
  ],

  "storage": [
    {
      "name": "Kingston NV2 250GB NVMe SSD",
      "brand": "Kingston",
      "type": "NVMe SSD",
      "capacity": "250GB",
      "estimatedPriceMYR": 99
    },
    {
      "name": "Kingston NV2 500GB NVMe SSD",
      "brand": "Kingston",
      "type": "NVMe SSD",
      "capacity": "500GB",
      "estimatedPriceMYR": 179
    },
    {
      "name": "Samsung 980 1TB NVMe SSD",
      "brand": "Samsung",
      "type": "NVMe SSD",
      "capacity": "1TB",
      "estimatedPriceMYR": 329
    },
    {
      "name": "WD Black SN850X 2TB",
      "brand": "Western Digital",
      "type": "NVMe SSD",
      "capacity": "2TB",
      "estimatedPriceMYR": 799
    },
    {
      "name": "Seagate Barracuda 2TB HDD",
      "brand": "Seagate",
      "type": "HDD",
      "capacity": "2TB",
      "estimatedPriceMYR": 249
    }
  ],

  "psu": [
    {
      "name": "Cooler Master MWE 450",
      "brand": "Cooler Master",
      "wattage": 450,
      "efficiency": "80+ Bronze",
      "estimatedPriceMYR": 179
    },
    {
      "name": "Cooler Master MWE 550",
      "brand": "Cooler Master",
      "wattage": 550,
      "efficiency": "80+ Bronze",
      "estimatedPriceMYR": 229
    },
    {
      "name": "Corsair CV650",
      "brand": "Corsair",
      "wattage": 650,
      "efficiency": "80+ Bronze",
      "estimatedPriceMYR": 299
    },
    {
      "name": "MSI MAG A750GL",
      "brand": "MSI",
      "wattage": 750,
      "efficiency": "80+ Gold",
      "estimatedPriceMYR": 459
    },
    {
      "name": "Corsair RM850x",
      "brand": "Corsair",
      "wattage": 850,
      "efficiency": "80+ Gold",
      "estimatedPriceMYR": 699
    }
  ],

  "case": [
    {
      "name": "Montech Air 100",
      "brand": "Montech",
      "formFactorSupport": ["Micro-ATX", "Mini-ITX"],
      "estimatedPriceMYR": 199
    },
    {
      "name": "NZXT H5 Flow",
      "brand": "NZXT",
      "formFactorSupport": ["ATX", "Micro-ATX", "Mini-ITX"],
      "estimatedPriceMYR": 399
    }
  ],

  "cpuCooler": [
    {
      "name": "Stock CPU Cooler",
      "brand": "AMD / Intel",
      "supportedSockets": ["AM4", "AM5", "LGA1200", "LGA1700"],
      "estimatedPriceMYR": 0
    },
    {
      "name": "Deepcool AK400",
      "brand": "Deepcool",
      "supportedSockets": ["AM4", "AM5", "LGA1200", "LGA1700"],
      "estimatedPriceMYR": 139
    }
  ],

  "monitor": [
    {
        "name": "Acer EK220Q 21.5 inch 75Hz",
        "brand": "Acer",
        "resolution": "1080p",
        "refreshRate": "75Hz",
        "useCase": ["study", "office"],
        "estimatedPriceMYR": 299
    },
    {
        "name": "AOC 24G4 24 inch 180Hz",
        "brand": "AOC",
        "resolution": "1080p",
        "refreshRate": "180Hz",
        "useCase": ["gaming"],
        "estimatedPriceMYR": 599
    },
    {
        "name": "LG UltraGear 27 inch 1440p 165Hz",
        "brand": "LG",
        "resolution": "1440p",
        "refreshRate": "165Hz",
        "useCase": ["gaming", "editing", "ai"],
        "estimatedPriceMYR": 1099
    }
]
}

# ==================== AI Service ====================

def call_ollama_ai(prompt):
    """Call Ollama AI. Try llama3 first, fallback to llama3.2:1b if it fails."""
    try:
        # First check if Ollama is running
        try:
            test = requests.get("http://localhost:11434/api/tags", timeout=5)
            if test.status_code != 200:
                return {"summary": "AI service not available. Start Ollama with: ollama serve"}
        except requests.exceptions.ConnectionError:
            return {"summary": "AI service not available. Start Ollama with: ollama serve"}

        # Try llama3 first, fallback to llama3.2:1b
        models_to_try = ["llama3", "llama3.2:1b"]

        for model in models_to_try:
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=120
                )

                if response.status_code == 200:
                    text = response.json()["response"]
                    return {"summary": text}

            except Exception:
                continue

        return {"summary": "AI models failed. Make sure you have run: ollama pull llama3"}

    except Exception as e:
        return {"summary": f"Ollama error: {str(e)}"}
    
def call_langchain_ai(prompt):

    if not LANGCHAIN_AVAILABLE:
        return call_ollama_ai(prompt)

    try:
        llm = OllamaLLM(
            model="llama3",
            temperature=0.3
        )

        short_prompt = f"""
You are an AI PC Builder assistant.
Reply in 100-150 words only.

{prompt}
"""

        response = llm.invoke(short_prompt)

        return {"summary": response}

    except Exception as e:
        return {"summary": f"LangChain error: {str(e)}"}

# ==================== Recommendation Engine ====================

def calculate_total_price(cpu, motherboard, gpu, ram, storage, psu, pc_case, cooler, monitor):
    total = (
        cpu["estimatedPriceMYR"] +
        motherboard["estimatedPriceMYR"] +
        gpu["estimatedPriceMYR"] +
        ram["estimatedPriceMYR"] +
        storage["estimatedPriceMYR"] +
        psu["estimatedPriceMYR"] +
        pc_case["estimatedPriceMYR"] +
        cooler["estimatedPriceMYR"] +
        monitor["estimatedPriceMYR"]
    )
    return total

def get_compatible_motherboard(mobo_list, cpu):
    compatible = []
    for mobo in mobo_list:
        socket_match = mobo["socket"] == cpu["socket"]
        memory_match = cpu["memoryType"] in mobo["memoryType"]
        if socket_match and memory_match:
            compatible.append(mobo)
    if not compatible:
        return None
    return compatible[0]

def get_best_motherboard(mobo_list, cpu):
    compatible = []
    for mobo in mobo_list:
        socket_match = mobo["socket"] == cpu["socket"]
        memory_match = cpu["memoryType"] in mobo["memoryType"]
        if socket_match and memory_match:
            compatible.append(mobo)
    if not compatible:
        return None
    return max(compatible, key=lambda x: x["estimatedPriceMYR"])

def get_compatible_ram(ram_list, cpu):
    compatible = []
    for ram in ram_list:
        if ram["memoryType"] == cpu["memoryType"]:
            compatible.append(ram)
    if not compatible:
        return None
    return compatible[0]

def get_best_ram(ram_list, cpu):
    compatible = []
    for ram in ram_list:
        if ram["memoryType"] == cpu["memoryType"]:
            compatible.append(ram)
    if not compatible:
        return None
    return max(compatible, key=lambda x: x["estimatedPriceMYR"])

def get_mid_ram(ram_list, cpu):
    """Pick middle-tier RAM"""
    compatible = []
    for ram in ram_list:
        if ram["memoryType"] == cpu["memoryType"]:
            compatible.append(ram)
    if not compatible:
        return None
    compatible.sort(key=lambda x: x["estimatedPriceMYR"])
    mid_index = len(compatible) // 2
    return compatible[mid_index]

def get_compatible_psu(psu_list, gpu):
    compatible = []
    for psu in psu_list:
        if psu["wattage"] >= gpu["recommendedPSU"]:
            compatible.append(psu)
    if not compatible:
        return None
    return compatible[0]

def get_best_psu(psu_list, gpu):
    compatible = []
    for psu in psu_list:
        if psu["wattage"] >= gpu["recommendedPSU"]:
            compatible.append(psu)
    if not compatible:
        return None
    return max(compatible, key=lambda x: x["wattage"])

def get_compatible_case(case_list, motherboard):
    compatible = []
    for pc_case in case_list:
        if motherboard["formFactor"] in pc_case["formFactorSupport"]:
            compatible.append(pc_case)
    if not compatible:
        return None
    return compatible[0]

def get_cpu_cooler(cooler_list, cpu):
    compatible = []
    for cooler in cooler_list:
        if cpu["socket"] in cooler["supportedSockets"]:
            compatible.append(cooler)
    if not compatible:
        return None
    return compatible[0]

def get_best_cooler(cooler_list, cpu):
    compatible = []
    for cooler in cooler_list:
        if cpu["socket"] in cooler["supportedSockets"]:
            compatible.append(cooler)
    if not compatible:
        return None
    return max(compatible, key=lambda x: x["estimatedPriceMYR"])

# ==================== Build Generator ====================

def pick_cpu_for_option(cpu_list, budget, option):
    """
    Pick CPU based on option:
    - performance: best CPU within 25% of budget
    - value: best CPU within 15% of budget
    - future: best CPU on AM5/LGA1700 within 20% of budget
    """
    if option == "performance":
        max_price = budget * 0.25
    elif option == "value":
        max_price = budget * 0.15
    elif option == "future":
        max_price = budget * 0.20
    else:
        max_price = budget * 0.25

    valid = []
    for cpu in cpu_list:
        if option == "future":
            if cpu["socket"] not in ["AM5", "LGA1700"]:
                continue
        if cpu["estimatedPriceMYR"] <= max_price:
            valid.append(cpu)

    if not valid:
        # Fallback: just get cheapest available
        if option == "future":
            future_cpus = [c for c in cpu_list if c["socket"] in ["AM5", "LGA1700"]]
            if future_cpus:
                return min(future_cpus, key=lambda x: x["estimatedPriceMYR"])
        return min(cpu_list, key=lambda x: x["estimatedPriceMYR"])

    return max(valid, key=lambda x: x["estimatedPriceMYR"])

def pick_gpu_for_option(gpu_list, budget, option):
    """
    Pick GPU based on option:
    - performance: best GPU within 35% of budget
    - value: best GPU within 20% of budget
    - future: best GPU within 30% of budget
    """
    if option == "performance":
        max_price = budget * 0.35
    elif option == "value":
        max_price = budget * 0.20
    elif option == "future":
        max_price = budget * 0.30
    else:
        max_price = budget * 0.35

    valid = []
    for gpu in gpu_list:
        if gpu["estimatedPriceMYR"] <= max_price:
            valid.append(gpu)

    if not valid:
        return min(gpu_list, key=lambda x: x["estimatedPriceMYR"])

    return max(valid, key=lambda x: x["estimatedPriceMYR"])

def pick_storage_for_option(storage_list, option):
    """Pick storage based on option"""
    ssds = [s for s in storage_list if s["type"] == "NVMe SSD"]
    ssds.sort(key=lambda x: x["estimatedPriceMYR"])

    if option == "performance":
        return ssds[-1] if ssds else storage_list[0]  # Best SSD
    elif option == "value":
        return ssds[0] if ssds else storage_list[0]   # Cheapest SSD
    else:
        # Future: 1TB SSD (middle ground)
        for s in ssds:
            if "1TB" in s["capacity"]:
                return s
        return ssds[1] if len(ssds) > 1 else ssds[0]

def generate_single_build(budget, option, purpose):
    """Generate one build. Returns (build_dict, error_string)."""
    data = PRODUCTS_DATA
    max_total = budget * 1.25  # Hard cap: never exceed budget + 25%

    cpu = pick_cpu_for_option(data["cpu"], budget, option)
    if not cpu:
        return None, "No suitable CPU found"

    # FIXED INDENTATION HERE
    if option == "future":
        # Pick mid-tier motherboard, not the most expensive
        compatible = []

        for mobo in data["motherboard"]:
            socket_match = mobo["socket"] == cpu["socket"]
            memory_match = cpu["memoryType"] in mobo["memoryType"]

            if socket_match and memory_match:
                compatible.append(mobo)

        if compatible:
            compatible.sort(key=lambda x: x["estimatedPriceMYR"])
            mid_index = len(compatible) // 2
            motherboard = compatible[mid_index]
        else:
            motherboard = None

    else:
        motherboard = get_compatible_motherboard(data["motherboard"], cpu)

    if not motherboard:
        return None, f"No compatible motherboard for {cpu['name']}"

    gpu = pick_gpu_for_option(data["gpu"], budget, option)

    if not gpu:
        return None, "No suitable GPU found"

    if option == "performance":
        ram = get_best_ram(data["ram"], cpu)

    elif option == "value":
        ram = get_compatible_ram(data["ram"], cpu)

    else:
        ram = get_mid_ram(data["ram"], cpu)

    if not ram:
        return None, f"No compatible RAM for {cpu['name']}"

    storage = pick_storage_for_option(data["storage"], option)

    if option == "future":
        psu = get_best_psu(data["psu"], gpu)
    else:
        psu = get_compatible_psu(data["psu"], gpu)

    if not psu:
        return None, f"No suitable PSU for {gpu['name']}"

    pc_case = get_compatible_case(data["case"], motherboard)

    if not pc_case:
        return None, f"No compatible case for {motherboard['name']}"

    if option == "performance":
        cooler = get_best_cooler(data["cpuCooler"], cpu)
    else:
        cooler = get_cpu_cooler(data["cpuCooler"], cpu)

    if not cooler:
        return None, f"No compatible cooler for {cpu['name']}"

    monitor = get_recommended_monitor(
        data["monitor"],
        purpose
    )

    total_price = calculate_total_price(
        cpu,
        motherboard,
        gpu,
        ram,
        storage,
        psu,
        pc_case,
        cooler,
        monitor
    )

    # If total exceeds max_total, try downgrading some parts
    if total_price > max_total:
        # Downgrade RAM to cheapest
        ram = get_compatible_ram(data["ram"], cpu)

        if ram:
            total_price = calculate_total_price(
                cpu,
                motherboard,
                gpu,
                ram,
                storage,
                psu,
                pc_case,
                cooler,
                monitor
            )

    if total_price > max_total:
        # Downgrade storage to cheapest SSD
        storage = pick_storage_for_option(data["storage"], "value")

        total_price = calculate_total_price(
            cpu,
            motherboard,
            gpu,
            ram,
            storage,
            psu,
            pc_case,
            cooler,
            monitor
        )

    if total_price > max_total:
        # Downgrade cooler to stock
        cooler = get_cpu_cooler(data["cpuCooler"], cpu)

        if cooler:
            total_price = calculate_total_price(
                cpu,
                motherboard,
                gpu,
                ram,
                storage,
                psu,
                pc_case,
                cooler,
                monitor
            )

    warnings = detect_red_flags(cpu, motherboard, gpu, ram, psu, pc_case)

    compatibility_score = calculate_compatibility_score(
        warnings,
        total_price,
        budget
    )

    bottleneck_result = detect_bottleneck(cpu, gpu)

    upgrade_advice = generate_upgrade_advice(
        cpu,
        motherboard,
        gpu,
        ram,
        psu
    )

    build = {
        "cpu": cpu,
        "motherboard": motherboard,
        "gpu": gpu,
        "ram": ram,
        "storage": storage,
        "psu": psu,
        "case": pc_case,
        "cpuCooler": cooler,
        "monitor": monitor,
        "budgetStatus": get_budget_status(total_price, budget),
        "totalPriceMYR": total_price,
        "compatibilityScore": compatibility_score,
        "redFlags": warnings,
        "bottleneckAnalysis": bottleneck_result,
        "upgradeAdvice": upgrade_advice,
    }

    build["installationGuide"] = generate_installation_guide(build)

    return build, None

# ==================== FastAPI Application ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 AI PC Builder API Started!")
    print("📍 API available at: http://127.0.0.1:8000")
    print("📖 API Documentation: http://127.0.0.1:8000/docs")
    yield
    print("👋 AI PC Builder API Shutting down...")

app = FastAPI(title="AI PC Builder API", lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "AI PC Builder System Running 🚀"}

@app.get("/build")
def generate_pc_build(
    budget: int,
    purpose: str = "gaming",
    preferred_brand: str = "any",
    need_wifi: bool = False,
    need_rgb: bool = False
):
    if budget < 2000:
        return JSONResponse(
            status_code=400,
            content={"error": "Minimum budget must be RM2000"}
        )

    # Generate 3 different builds
    build_a, error_a = generate_single_build(budget, "performance", purpose)
    build_b, error_b = generate_single_build(budget, "value", purpose)
    build_c, error_c = generate_single_build(budget, "future", purpose)

    options = {}

    if build_a:
        options["optionA"] = {
            "name": "🏆 Best Performance",
            "description": "Maximum performance with the best CPU and GPU within budget",
            **build_a
        }

    if build_b:
        options["optionB"] = {
            "name": "💰 Best Value",
            "description": "Save money while keeping good performance",
            **build_b
        }

    if build_c:
        options["optionC"] = {
            "name": "🔮 Future Proof",
            "description": "Newest platform with easy upgrade path for later",
            **build_c
        }

    if not options:
        return JSONResponse(
            status_code=404,
            content={"error": "Could not generate any builds for this budget. Try a higher budget."}
        )

    # AI explanation
    ai_parts = []
    for key, opt in options.items():
        ai_parts.append(f"{opt['name']}: CPU={opt['cpu']['name']}, GPU={opt['gpu']['name']}, RAM={opt['ram']['name']}, Total=RM{opt['totalPriceMYR']}")

    ai_prompt = f"""You are a PC Build Advisor. Your response must be between 100 to 150 words total. No more, no less.

Budget: RM{budget} | Purpose: {purpose}

{chr(10).join(ai_parts)}

Reply in EXACTLY this format (3-4 sentences each):
OPTION A: (explain why pick this build, pros and cons)
OPTION B: (explain why pick this build, pros and cons)
OPTION C: (explain why pick this build, pros and cons)"""

    ai_result = call_langchain_ai(ai_prompt)

    build_type = get_build_type_label(purpose)
    cache_key = f"{budget}-{purpose}-{preferred_brand}-{need_wifi}-{need_rgb}"
    
    if cache_key in BUILD_CACHE:
        return BUILD_CACHE[cache_key]

    result = {
        "buildType": build_type,
        "budget": budget,
        "purpose": purpose,
        "preferredBrand": preferred_brand,
        "needWifi": need_wifi,
        "needRGB": need_rgb,
        "options": options,
        "aiExplanation": ai_result,
        "errors": {
            "optionA": error_a,
            "optionB": error_b,
            "optionC": error_c
        }
    }

    BUILD_CACHE[cache_key] = result
    return result

@app.get("/budget-options")
def budget_options(budget: int):
    if budget < 2000:
        return JSONResponse(
            status_code=400,
            content={"error": "Minimum budget must be RM2000"}
        )

    return {
        "budget": budget,
        "options": [
            {
                "option": "A",
                "name": "Best Performance",
                "description": "Uses more budget on GPU and CPU for gaming and editing."
            },
            {
                "option": "B",
                "name": "Cheapest Compatible",
                "description": "Chooses the lowest cost compatible parts."
            },
            {
                "option": "C",
                "name": "Future Upgrade Friendly",
                "description": "Chooses better motherboard and PSU for future upgrades."
            }
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/components")
def list_components():
    return {
        "cpu_count": len(PRODUCTS_DATA["cpu"]),
        "motherboard_count": len(PRODUCTS_DATA["motherboard"]),
        "gpu_count": len(PRODUCTS_DATA["gpu"]),
        "ram_count": len(PRODUCTS_DATA["ram"]),
        "storage_count": len(PRODUCTS_DATA["storage"]),
        "psu_count": len(PRODUCTS_DATA["psu"]),
        "case_count": len(PRODUCTS_DATA["case"]),
        "cooler_count": len(PRODUCTS_DATA["cpuCooler"]),
        "monitor_count": len(PRODUCTS_DATA["monitor"])
    }

# ==================== Smart AI Agent Features ====================

def get_recommended_monitor(monitor_list, purpose):
    for monitor in monitor_list:
        monitor_purpose = monitor.get("purpose", monitor.get("useCase", []))

        if purpose in monitor_purpose:
            return monitor

    return monitor_list[0]

def get_budget_status(total_price, budget):
    if total_price <= budget:
        return "🟢 Within Budget"
    else:
        return "🔴 Over Budget"
    
def detect_red_flags(cpu, motherboard, gpu, ram, psu, pc_case):
    warnings = []

    if cpu["socket"] != motherboard["socket"]:
        warnings.append("CPU socket is not compatible with motherboard.")

    if cpu["memoryType"] not in motherboard["memoryType"]:
        warnings.append("CPU RAM type does not match motherboard RAM support.")

    if ram["memoryType"] != cpu["memoryType"]:
        warnings.append("RAM type does not match CPU memory type.")

    if psu["wattage"] < gpu["recommendedPSU"]:
        warnings.append("PSU wattage is too low for the selected GPU.")

    if motherboard["formFactor"] not in pc_case["formFactorSupport"]:
        warnings.append("Case does not support the motherboard form factor.")

    return warnings

def calculate_compatibility_score(warnings, total_price, budget):
    score = 100
    score -= len(warnings) * 15
    if total_price > budget:
        score -= 20
    if total_price > budget * 0.95:
        score -= 5
    if score < 0:
        score = 0
    return score

def get_build_type_label(purpose):
    if purpose == "gaming":
        return "Gaming Performance Build"
    elif purpose == "editing":
        return "Content Creation Build"
    elif purpose == "ai":
        return "AI / Machine Learning Build"
    elif purpose == "study":
        return "Student Budget Build"
    else:
        return "Balanced PC Build"
    
def detect_bottleneck(cpu, gpu):
    cpu_name = cpu["name"].lower()
    gpu_name = gpu["name"].lower()

    # Weak CPU + Strong GPU
    if (
        ("ryzen 3" in cpu_name or "i3" in cpu_name)
        and
        ("4070" in gpu_name or "7800 xt" in gpu_name)
    ):
        return "⚠️ Possible GPU bottleneck: CPU may limit GPU performance."

    # Strong CPU + Weak GPU
    if (
        ("ryzen 9" in cpu_name or "i9" in cpu_name)
        and
        ("1650" in gpu_name)
    ):
        return "⚠️ Possible GPU underutilization: GPU is too weak for this CPU."

    return "✅ No major bottleneck detected."

def generate_upgrade_advice(cpu, motherboard, gpu, ram, psu):

    advice = []

    # Platform upgrade advice
    if cpu["socket"] == "AM4":
        advice.append("🔄 AM4 platform has limited future upgrades. Consider AM5 for longer lifespan.")

    if cpu["socket"] == "AM5":
        advice.append("🚀 AM5 platform supports future Ryzen upgrades.")

    if cpu["socket"] == "LGA1700":
        advice.append("🚀 LGA1700 platform supports newer Intel generations.")

    # RAM advice
    if ram["memoryType"] == "DDR4":
        advice.append("🧠 DDR5 RAM can improve future performance and upgrade flexibility.")

    # PSU advice
    if psu["wattage"] < 650:
        advice.append("⚡ Consider upgrading to 650W+ PSU for future GPU upgrades.")

    # GPU advice
    gpu_name = gpu["name"].lower()

    if "1650" in gpu_name:
        advice.append("🎮 Future GPU upgrade recommended for modern AAA gaming.")

    if "3060" in gpu_name:
        advice.append("🎮 RTX 4070 class GPU could improve future AI and rendering performance.")

    if not advice:
        advice.append("✅ This build already has a strong upgrade path.")

    return advice
def generate_installation_guide(build):
    cpu = build["cpu"]["name"]
    motherboard = build["motherboard"]["name"]
    gpu = build["gpu"]["name"]
    ram = build["ram"]["name"]
    storage = build["storage"]["name"]
    psu = build["psu"]["name"]
    pc_case = build["case"]["name"]
    cooler = build["cpuCooler"]["name"]
    monitor = build["monitor"]["name"]

    guide = f"""
🛠️ AI PC Assembly Guide

1. Prepare workspace
- Turn off power.
- Use anti-static precautions.
- Place the {motherboard} on its box.

2. Install CPU
- Open the CPU socket.
- Align and install {cpu}.
- Lock the socket carefully.

3. Install RAM
- Insert {ram} into the motherboard RAM slot.
- Press until both clips lock.

4. Install storage
- Install {storage} into the M.2 slot or storage bay.

5. Install CPU cooler
- Mount {cooler} on the CPU.
- Connect cooler fan cable to CPU_FAN header.

6. Install motherboard into case
- Place motherboard into {pc_case}.
- Screw it properly into standoffs.

7. Install PSU
- Mount {psu} into the case.
- Connect 24-pin motherboard cable and CPU power cable.

8. Install GPU
- Insert {gpu} into PCIe x16 slot.
- Screw it to the case.
- Connect PCIe power cable if needed.

9. Connect monitor
- Connect {monitor} to the GPU display port/HDMI.

10. Final check
- Check all cables.
- Turn on PC.
- Enter BIOS.
- Install Windows and drivers.

⚠️ Safety: Do not force components. If unsure, check the motherboard manual.
"""
    return guide

# ==================== Menu System ====================

def run_api_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

def print_build_option(label, opt):
    print(f"\n  {opt['name']} ({opt['budgetStatus']})")
    print(f"  {opt['description']}")
    print(f"  {'─' * 40}")

    print(f"  💰 Total Price: RM{opt['totalPriceMYR']}")
    print(f"  💻 CPU: {opt['cpu']['name']} (RM{opt['cpu']['estimatedPriceMYR']})")
    print(f"  🖥️  Motherboard: {opt['motherboard']['name']} (RM{opt['motherboard']['estimatedPriceMYR']})")
    print(f"  🎮 GPU: {opt['gpu']['name']} (RM{opt['gpu']['estimatedPriceMYR']})")
    print(f"  🧠 RAM: {opt['ram']['name']} (RM{opt['ram']['estimatedPriceMYR']})")
    print(f"  💾 Storage: {opt['storage']['name']} (RM{opt['storage']['estimatedPriceMYR']})")
    print(f"  ⚡ PSU: {opt['psu']['name']} (RM{opt['psu']['estimatedPriceMYR']})")
    print(f"  📦 Case: {opt['case']['name']} (RM{opt['case']['estimatedPriceMYR']})")
    print(f"  ❄️  Cooler: {opt['cpuCooler']['name']} (RM{opt['cpuCooler']['estimatedPriceMYR']})")
    print(f"  🖥️  Monitor: {opt['monitor']['name']} (RM{opt['monitor']['estimatedPriceMYR']})")
    print(f"  ✅ Compatibility: {opt['compatibilityScore']}%")
    print(f"\n  🧠 Bottleneck Analysis: {opt['bottleneckAnalysis']}")
    print(f"     {opt['bottleneckAnalysis']}")

    print("\n  🔧 Upgrade Advice:")
    for advice in opt['upgradeAdvice']:
        print(f"     {advice}")

    if opt['redFlags']:
        for flag in opt['redFlags']:
            print(f"  ⚠️  {flag}")

def run_menu():
    BASE_URL = "http://127.0.0.1:8000"

    print("=" * 50)
    print("🎮 Welcome to AI PC Builder System 🚀")
    print("=" * 50)

    print("⏳ Waiting for API server to start...")
    time.sleep(2)

    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ API server is ready!\n")
                break
        except requests.exceptions.ConnectionError:
            if i == max_retries - 1:
                print("❌ Could not connect to API server. Please restart the application.")
                return
            time.sleep(1)

    while True:
        print("\n" + "=" * 40)
        print("AI PC BUILDER MENU")
        print("=" * 40)
        print("1. 🔧 Build Your New PC")
        print("2. 📋 View Available Components")
        print("3. ❤️  Health Check")
        print("4. 🚪 Exit")
        print("-" * 40)

        try:
            choice = int(input("\nEnter your choice (1-4): "))

            if choice == 1:
                try:
                    budget = int(input("💰 Enter your budget (RM): "))

                    print("\n🎯 What is the purpose of this PC?")
                    print("1. 🎮 Gaming")
                    print("2. 🤖 AI / Machine Learning")
                    print("3. 📚 Study / Office")

                    purpose_choice = input("\nEnter your choice (1-3): ").strip()

                    if purpose_choice == "1":
                        purpose = "gaming"
                    elif purpose_choice == "2":
                        purpose = "ai"
                    elif purpose_choice == "3":
                        purpose = "study"
                    else:
                        print("⚠️ Invalid choice, defaulting to Gaming.")
                        purpose = "gaming"

                    print(f"\n🔨 Generating 3 build options for RM{budget} ({purpose})...")
                    print("⏳ This may take a moment (AI is thinking)...\n")

                    response = requests.get(f"{BASE_URL}/build?budget={budget}&purpose={purpose}", timeout=180)

                    if response.status_code == 200:
                        result = response.json()
                        options = result.get("options", {})

                        print("=" * 50)
                        print(f"✅ BUILD OPTIONS FOR RM{budget}")
                        print("=" * 50)

                        if "optionA" in options:
                            print_build_option("A", options["optionA"])

                        if "optionB" in options:
                            print_build_option("B", options["optionB"])

                        if "optionC" in options:
                            print_build_option("C", options["optionC"])
                        
                        print("\n" + "=" * 50)
                        print("🛠️ AI INSTALLATION GUIDE")
                        print("=" * 50)
                        
                        first_option = next(iter(options.values()))
                        print(first_option["installationGuide"])

                        print("\n" + "=" * 50)
                        print("🤖 AI RECOMMENDATION:")
                        print("-" * 50)
                        ai_exp = result.get("aiExplanation", {})
                        print(ai_exp.get("summary", "AI not available"))
                        print("=" * 50)

                    else:
                        error_data = response.json()
                        print(f"❌ Error: {error_data.get('error', 'Unknown error')}")

                except ValueError:
                    print("❌ Please enter a valid number for budget")
                except requests.exceptions.ConnectionError:
                    print("❌ Cannot connect to server. Make sure the application is running properly!")

            elif choice == 2:
                try:
                    response = requests.get(f"{BASE_URL}/components", timeout=5)
                    if response.status_code == 200:
                        components = response.json()
                        print("\n📦 AVAILABLE COMPONENTS:")
                        print("-" * 30)
                        print(f"🖥️ CPUs: {components['cpu_count']}")
                        print(f"🔌 Motherboards: {components['motherboard_count']}")
                        print(f"🎮 GPUs: {components['gpu_count']}")
                        print(f"🧠 RAM: {components['ram_count']}")
                        print(f"💾 Storage: {components['storage_count']}")
                        print(f"⚡ PSUs: {components['psu_count']}")
                        print(f"📦 Cases: {components['case_count']}")
                        print(f"❄️ CPU Coolers: {components['cooler_count']}")
                    else:
                        print("❌ Failed to fetch components")
                except requests.exceptions.ConnectionError:
                    print("❌ Cannot connect to server")

            elif choice == 3:
                try:
                    response = requests.get(f"{BASE_URL}/health", timeout=5)
                    if response.status_code == 200:
                        print("✅ System is healthy and running!")
                    else:
                        print("⚠️ System status unknown")
                except requests.exceptions.ConnectionError:
                    print("❌ Cannot connect to server")

            elif choice == 4:
                print("\n👋 Thank you for using AI PC Builder. Goodbye!")
                print("💡 Tip: You can also access the API at http://127.0.0.1:8000/docs")
                break
            else:
                print("❌ Invalid choice. Please enter 1-4.")

        except ValueError:
            print("❌ Please enter a number between 1-4")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break

# ==================== Main Entry Point ====================

if __name__ == "__main__":
    import sys

    print("""
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║         AI PC BUILDER SYSTEM v1.0                    ║
    ║         Complete Integrated Solution                 ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    """)

    print("Starting system...")
    print("This will start both the API server and menu interface.")
    print("Press Ctrl+C to stop the server at any time.\n")

    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()

    try:
        run_menu()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down AI PC Builder System...")
        sys.exit(0)