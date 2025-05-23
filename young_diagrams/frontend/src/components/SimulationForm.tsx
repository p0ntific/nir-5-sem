import React, { useState } from "react";
import FlexBox from "../ui-kit/FlexBox";

interface ISimulationFormProps {
    onSubmit: (params: any) => void;
    isLoading: boolean;
    defaultParams: {
        steps: number;
        alpha: number;
        runs: number;
    };
}

const SimulationForm: React.FC<ISimulationFormProps> = ({
    onSubmit,
    isLoading,
    defaultParams,
}) => {
    const [steps, setSteps] = useState<string>("500");
    const [alpha, setAlpha] = useState<string>("0.5");
    const [runs, setRuns] = useState<string>("5");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit({
            steps: steps === "" ? defaultParams.steps : Number(steps),
            alpha: alpha === "" ? defaultParams.alpha : Number(alpha),
            runs: runs === "" ? defaultParams.runs : Number(runs),
        });
    };

    return (
        <form className="visualization-container" onSubmit={handleSubmit}>
            <FlexBox direction="column" padding={24} gap={24}>
                <h2>Параметры симуляции</h2>

                <FlexBox direction="column" gap={16}>
                    <label>
                        <div style={{ marginBottom: "8px" }}>
                            Количество шагов (10-5000)
                        </div>
                        <input
                            type="number"
                            min={10}
                            max={5000}
                            value={steps}
                            onChange={(e) => setSteps(e.target.value)}
                            placeholder={defaultParams.steps.toString()}
                            required
                        />
                    </label>

                    <label>
                        <div style={{ marginBottom: "8px" }}>
                            Параметр α (0.1-5.0)
                            <div
                                style={{
                                    fontSize: "0.8rem",
                                    color: "var(--text-muted)",
                                }}
                            >
                                Влияет на скорость роста диаграммы
                            </div>
                        </div>
                        <input
                            type="number"
                            min={0.1}
                            max={5.0}
                            step={0.1}
                            value={alpha}
                            onChange={(e) => setAlpha(e.target.value)}
                            placeholder={defaultParams.alpha.toString()}
                            required
                        />
                    </label>

                    <label>
                        <div style={{ marginBottom: "8px" }}>
                            Количество запусков (1-10)
                            <div
                                style={{
                                    fontSize: "0.8rem",
                                    color: "var(--text-muted)",
                                }}
                            >
                                Больше запусков - более точный результат
                            </div>
                        </div>
                        <input
                            type="number"
                            min={1}
                            max={10}
                            value={runs}
                            onChange={(e) => setRuns(e.target.value)}
                            placeholder={defaultParams.runs.toString()}
                            required
                        />
                    </label>
                </FlexBox>

                <button
                    type="submit"
                    className="primary"
                    disabled={isLoading}
                    style={{ position: "relative" }}
                >
                    {isLoading ? (
                        <>
                            <span style={{ opacity: 0.7 }}>Симуляция...</span>
                            <div className="button-loader"></div>
                        </>
                    ) : (
                        "Запустить симуляцию"
                    )}
                </button>
            </FlexBox>
        </form>
    );
};

export { SimulationForm };
