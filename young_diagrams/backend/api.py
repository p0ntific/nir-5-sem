from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Set, Union, Tuple
import json
import os
import uvicorn
import numpy as np
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from PIL import Image

from diagrams2d import DiagramSimulator2D
from diagrams3d import DiagramSimulator3D
from common.utils import save_cells_to_file

# FastAPI app
app = FastAPI(title="Young Diagrams API",
              description="API для симуляции и визуализации диаграмм Юнга",
              version="1.0.0")

# Добавляем CORS middleware для обработки запросов с разных источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники (в продакшене лучше указать конкретные)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных для API
class SimulationParams2D(BaseModel):
    steps: int = Field(100, ge=10, le=5000, description="Количество шагов симуляции")
    alpha: float = Field(1.0, ge=0.1, le=5.0, description="Параметр альфа для распределения")
    algorithm: str = Field("random", description="Алгоритм симуляции (random или plancherel)")
    runs: int = Field(1, ge=1, le=10, description="Количество повторений для агрегирования данных")

class SimulationParams3D(BaseModel):
    steps: int = Field(100, ge=10, le=5000, description="Количество шагов симуляции")
    alpha: float = Field(1.0, ge=0.1, le=5.0, description="Параметр альфа для распределения")
    algorithm: str = Field("random", description="Алгоритм симуляции (random или plancherel)")
    beta: Optional[float] = Field(1.0, ge=0.1, le=5.0, description="Параметр бета для распределения (для 3D)")
    gamma: Optional[float] = Field(1.0, ge=0.1, le=5.0, description="Параметр гамма для распределения (для 3D)")
    runs: int = Field(1, ge=1, le=10, description="Количество повторений для агрегирования данных")

# Глобальные переменные для хранения результатов последних симуляций
last_2d_simulation = None
last_3d_simulation = None

# Endpoint для проверки статуса API (health check)
@app.get("/")
async def root():
    """Корневой endpoint API"""
    return {
        "message": "Добро пожаловать в API для моделирования диаграмм Юнга!",
        "version": "1.0.0",
        "status": "ok"
    }

# Более детальный endpoint для проверки статуса
@app.get("/status")
async def check_status():
    """Проверка статуса API"""
    return {
        "status": "ok",
        "message": "API работает",
        "version": "1.0.0"
    }

# API для 2D диаграмм
@app.post("/simulate/2d")
async def simulate_2d(params: SimulationParams2D):
    """Запуск симуляции 2D диаграммы Юнга"""
    global last_2d_simulation
    
    try:
        print(f"Starting 2D simulation with params: {params}")
        # Создаем экземпляр симулятора
        simulator = DiagramSimulator2D()
        
        # Запускаем симуляцию
        simulator.simulate(
            n_steps=params.steps,
            alpha=params.alpha,
            runs=params.runs
        )
        
        # Получаем результаты
        result = simulator.get_json_data()
        print(f"Result from 2D simulation: {result}")
        
        # Сохраняем результат в глобальную переменную
        last_2d_simulation = result
        
        # Преобразуем ячейки в формат, который нужен фронтенду
        cells = []
        if "cells" in result and isinstance(result["cells"], list):
            for cell in result["cells"]:
                if isinstance(cell, dict) and "x" in cell and "y" in cell:
                    cells.append({
                        "x": cell["x"],
                        "y": cell["y"],
                        "value": cell.get("normalized_count", 1.0)
                    })
        else:
            # Если cells не в ожидаемом формате, пытаемся использовать другой формат
            print("Cell format unexpected, using alternative parsing")
            for cell in result.get("cells", []):
                if isinstance(cell, (list, tuple)) and len(cell) >= 2:
                    cells.append({
                        "x": cell[0],
                        "y": cell[1],
                        "value": 1.0
                    })
        
        if not cells and 'error' not in result:
            # Если ячеек нет, но ошибки тоже нет, возможно, формат другой
            # Пытаемся получить данные непосредственно из total_cell_counts
            print("No cells in standard format, attempting direct access")
            # Для отладки - проверяем, что есть в симуляторе
            print(f"Total cell counts: {simulator.total_cell_counts}")
            
            if simulator.total_cell_counts:
                for (x, y), count in simulator.total_cell_counts.items():
                    cells.append({
                        "x": x,
                        "y": y,
                        "value": 1.0
                    })
        
        if not cells:
            raise ValueError("Ошибка при обработке данных ячеек")
            
        return {"cells": cells, "status": "success"}
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Ошибка в simulate_2d: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при симуляции: {str(e)}"
        )

@app.get("/visualize/2d")
async def visualize_2d():
    """Визуализация последней 2D симуляции"""
    global last_2d_simulation
    
    if not last_2d_simulation:
        raise HTTPException(
            status_code=404,
            detail="Нет доступных данных симуляции. Запустите симуляцию сначала."
        )
    
    try:
        # Преобразуем ячейки в формат, который нужен фронтенду
        cells = []
        if "cells" in last_2d_simulation and isinstance(last_2d_simulation["cells"], list):
            for cell in last_2d_simulation["cells"]:
                if isinstance(cell, dict) and "x" in cell and "y" in cell:
                    cells.append({
                        "x": cell["x"],
                        "y": cell["y"],
                        "value": cell.get("normalized_count", 1.0)
                    })
        
        if not cells:
            raise ValueError("Ошибка при обработке данных ячеек")
            
        return {"cells": cells, "status": "success"}
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Ошибка в visualize_2d: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при визуализации: {str(e)}"
        )

@app.get("/limit-shape/2d")
async def get_limit_shape_2d_api():
    try:
        # Создаем симулятор
        simulator = DiagramSimulator2D()
        
        # Создаем визуализацию предельной формы
        fig = simulator.limit_shape_visualize()
        
        # Сохраняем изображение в формате base64
        buf = io.BytesIO()
        FigureCanvas(fig).print_png(buf)
        buf.seek(0)
        
        # Кодируем изображение в base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        return {"image": f"data:image/png;base64,{img_str}"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении предельной формы: {str(e)}"
        )

# API для 3D диаграмм
@app.post("/simulate/3d")
async def simulate_3d(params: SimulationParams3D):
    """Запуск симуляции 3D диаграммы Юнга"""
    global last_3d_simulation
    
    try:
        print(f"Starting 3D simulation with params: {params}")
        # Создаем экземпляр симулятора
        simulator = DiagramSimulator3D()
        
        # Запускаем симуляцию - передаём только те параметры, которые поддерживает метод
        # Убираем все параметры, которые не поддерживаются
        simulator.simulate(
            n_steps=params.steps,
            alpha=params.alpha,
            runs=params.runs
        )
        
        # Получаем результаты
        result = simulator.get_json_data()
        print(f"Result from 3D simulation: {result}")
        
        # Сохраняем результат в глобальную переменную
        last_3d_simulation = result
        
        # Преобразуем ячейки в формат, который нужен фронтенду
        cells = []
        if "cells" in result and isinstance(result["cells"], list):
            for cell in result["cells"]:
                if isinstance(cell, dict) and "x" in cell and "y" in cell and "z" in cell:
                    cells.append({
                        "x": cell["x"],
                        "y": cell["y"],
                        "z": cell["z"],
                        "value": cell.get("normalized_count", 1.0)
                    })
                elif isinstance(cell, (list, tuple)) and len(cell) >= 3:
                    cells.append({
                        "x": cell[0],
                        "y": cell[1],
                        "z": cell[2],
                        "value": 1.0
                    })
        else:
            # Если cells не в ожидаемом формате, пытаемся использовать другой формат
            print("Cell format unexpected, using alternative parsing")
            # Для отладки - проверяем, что есть в симуляторе
            print(f"Total cell counts: {simulator.total_cell_counts}")
            
            if simulator.total_cell_counts:
                for (x, y, z), count in simulator.total_cell_counts.items():
                    cells.append({
                        "x": x,
                        "y": y,
                        "z": z,
                        "value": 1.0
                    })
        
        if not cells:
            raise ValueError("Ошибка при обработке данных ячеек")
            
        return {"cells": cells, "status": "success"}
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Ошибка в simulate_3d: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при симуляции: {str(e)}"
        )

@app.get("/visualize/3d/{viz_type}")
async def visualize_3d(viz_type: str):
    """
    Визуализация последней 3D симуляции
    
    viz_type может быть одним из: solid, wireframe, heatmap
    """
    global last_3d_simulation
    
    if not last_3d_simulation:
        raise HTTPException(
            status_code=404,
            detail="Нет доступных данных симуляции. Запустите симуляцию сначала."
        )
    
    try:
        # Преобразуем ячейки в формат, который нужен фронтенду
        cells = []
        if "cells" in last_3d_simulation and isinstance(last_3d_simulation["cells"], list):
            for cell in last_3d_simulation["cells"]:
                if isinstance(cell, dict) and "x" in cell and "y" in cell and "z" in cell:
                    cells.append({
                        "x": cell["x"],
                        "y": cell["y"],
                        "z": cell["z"],
                        "value": cell.get("normalized_count", 1.0)
                    })
                elif isinstance(cell, (list, tuple)) and len(cell) >= 3:
                    cells.append({
                        "x": cell[0],
                        "y": cell[1],
                        "z": cell[2],
                        "value": 1.0
                    })
        
        if not cells:
            raise ValueError("Ошибка при обработке данных ячеек")
            
        return {"cells": cells, "status": "success", "visualization_type": viz_type}
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Ошибка в visualize_3d: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при визуализации: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 