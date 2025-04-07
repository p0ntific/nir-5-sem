import { useState, useCallback } from "react";

export interface ICell2D {
    x: number;
    y: number;
    value: number;
}

export interface ISimulationParams2D {
    steps: number;
    alpha: number;
    runs: number; // Количество запусков для симуляции
}

const DEFAULT_PARAMS: ISimulationParams2D = {
    steps: 1000,
    alpha: 0.5,
    runs: 1,
};

// API URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export const useSimulation2D = () => {
    const [cells, setCells] = useState<ICell2D[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [simulationParams, setSimulationParams] =
        useState<ISimulationParams2D>(DEFAULT_PARAMS);
    const [isSimulationCompleted, setIsSimulationCompleted] =
        useState<boolean>(false);

    const startSimulation = useCallback(async (params: ISimulationParams2D) => {
        setIsLoading(true);
        setError(null);
        setSimulationParams(params);
        setIsSimulationCompleted(false);

        try {
            console.log("Starting 2D simulation with params:", params);

            // Симуляция на сервере
            const response = await fetch(`${API_BASE_URL}/simulate/2d`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    ...params,
                    runs: params.runs || 1,
                    algorithm: "random", // Устанавливаем algorithm по умолчанию, но не показываем в UI
                }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(
                    `Ошибка при запуске симуляции: ${response.status} ${response.statusText}. ${errorText}`
                );
            }

            const simulationData = await response.json();
            console.log("Simulation data:", simulationData);

            if (simulationData.cells && Array.isArray(simulationData.cells)) {
                setCells(simulationData.cells);
                setIsSimulationCompleted(true);
            } else {
                // Если нет прямого ответа с ячейками, делаем дополнительный запрос на визуализацию
                const visualizationResponse = await fetch(
                    `${API_BASE_URL}/visualize/2d`
                );
                if (!visualizationResponse.ok) {
                    const errorText = await visualizationResponse.text();
                    throw new Error(
                        `Ошибка при получении визуализации: ${visualizationResponse.status} ${visualizationResponse.statusText}. ${errorText}`
                    );
                }

                const visualizationData = await visualizationResponse.json();
                console.log("Visualization data:", visualizationData);

                if (
                    visualizationData.cells &&
                    Array.isArray(visualizationData.cells)
                ) {
                    setCells(visualizationData.cells);
                    setIsSimulationCompleted(true);
                } else {
                    throw new Error("Полученные данные имеют неверный формат");
                }
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Неизвестная ошибка");
            console.error("API Error:", err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    return {
        cells,
        isLoading,
        error,
        simulationParams,
        startSimulation,
        isSimulationCompleted,
    };
};
