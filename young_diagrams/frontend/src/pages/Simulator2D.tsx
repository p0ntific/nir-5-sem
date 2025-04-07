import React from "react";
import FlexBox from "../ui-kit/FlexBox";
import { SimulationForm } from "../components/SimulationForm";
import VisualizationCanvas2D from "../components/VisualizationCanvas2D";
import { useSimulation2D } from "../hooks/useSimulation2D";
import Header from "../components/Header";

const Simulator2D: React.FC = () => {
    const { cells, isLoading, error, simulationParams, startSimulation } =
        useSimulation2D();

    return (
        <FlexBox direction="column" style={{ minHeight: "100vh" }}>
            <Header />
            <FlexBox
                direction="column"
                padding={40}
                gap={40}
                align="center"
                style={{
                    maxWidth: "1200px",
                    margin: "0 auto",
                    width: "100%",
                }}
            >
                <section style={{ width: "100%", textAlign: "center" }}>
                    <h1>2D Симулятор диаграмм Юнга</h1>
                    <p
                        className="text-muted"
                        style={{
                            margin: "0 auto",
                        }}
                    >
                        Настройте параметры и запустите симуляцию для
                        визуализации двумерных диаграмм Юнга
                    </p>
                </section>

                <FlexBox
                    gap={32}
                    direction={"row"}
                    style={{ width: "100%" }}
                    align="stretch"
                >
                    <FlexBox
                        direction="column"
                        style={{ flex: 1, minWidth: "300px" }}
                    >
                        <SimulationForm
                            onSubmit={startSimulation}
                            isLoading={isLoading}
                            defaultParams={simulationParams}
                        />
                    </FlexBox>

                    <FlexBox direction="column" gap={24} style={{ flex: 2 }}>
                        <div
                            className="visualization-container"
                            style={{ padding: "8px", width: "700px" }}
                        >
                            <FlexBox
                                justify="space-between"
                                align="center"
                                padding={16}
                            >
                                <h2 style={{ margin: 0 }}>Визуализация</h2>
                            </FlexBox>

                            <FlexBox style={{ height: "500px", width: "100%" }}>
                                {error ? (
                                    <FlexBox
                                        justify="center"
                                        align="center"
                                        style={{
                                            width: "100%",
                                            color: "var(--error-color)",
                                        }}
                                    >
                                        {error}
                                    </FlexBox>
                                ) : (
                                    <VisualizationCanvas2D
                                        cells={cells}
                                        isLoading={isLoading}
                                        simulationParams={simulationParams}
                                    />
                                )}
                            </FlexBox>
                        </div>
                    </FlexBox>
                </FlexBox>
            </FlexBox>
        </FlexBox>
    );
};

export default Simulator2D;
