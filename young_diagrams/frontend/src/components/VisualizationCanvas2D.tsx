import React, { useRef, useState, useEffect } from "react";
import { Stage, Layer, Rect, Text, Line, Group } from "react-konva";
import { ICell2D } from "../hooks/useSimulation2D";
import FlexBox from "../ui-kit/FlexBox";

export interface IVisualizationCanvas2DProps {
    cells: ICell2D[];
    simulationParams: {
        steps: number;
        alpha: number;
        runs: number;
    };
    isLoading: boolean;
}

const VisualizationCanvas2D: React.FC<IVisualizationCanvas2DProps> = ({
    cells,
    simulationParams,
    isLoading,
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [stageWidth, setStageWidth] = useState(800);
    const [stageHeight, setStageHeight] = useState(600);
    const [scale, setScale] = useState(0.34);
    const [position, setPosition] = useState({ x: 0, y: 0 });

    // Размер клетки и отступы
    const cellSize = 30;
    const padding = 40;

    // Обновляем размеры Stage при изменении размера контейнера
    useEffect(() => {
        if (!containerRef.current) return;

        const updateDimensions = () => {
            if (containerRef.current) {
                setStageWidth(containerRef.current.offsetWidth);
                setStageHeight(containerRef.current.offsetHeight);
            }
        };

        updateDimensions();
        window.addEventListener("resize", updateDimensions);

        return () => window.removeEventListener("resize", updateDimensions);
    }, []);

    // Обработчик колесика мыши для масштабирования
    const handleWheel = (e: any) => {
        e.evt.preventDefault();

        const scaleBy = 1.1;
        const stage = e.target.getStage();
        const oldScale = stage.scaleX();

        // Получаем позицию курсора относительно stage
        const mousePointTo = {
            x: stage.getPointerPosition().x / oldScale - stage.x() / oldScale,
            y: stage.getPointerPosition().y / oldScale - stage.y() / oldScale,
        };

        // Вычисляем новый масштаб
        const newScale =
            e.evt.deltaY < 0 ? oldScale * scaleBy : oldScale / scaleBy;

        // Ограничиваем масштаб минимальным и максимальным значениями
        const limitedScale = Math.max(0.1, Math.min(newScale, 10));

        // Обновляем состояние масштаба и позиции
        setScale(limitedScale);
        setPosition({
            x:
                (stage.getPointerPosition().x / limitedScale - mousePointTo.x) *
                limitedScale,
            y:
                (stage.getPointerPosition().y / limitedScale - mousePointTo.y) *
                limitedScale,
        });
    };

    // Получаем максимальные координаты клеток для определения размера диаграммы
    const maxCoordinates = cells.reduce(
        (max, cell) => ({
            x: Math.max(max.x, cell.x),
            y: Math.max(max.y, cell.y),
        }),
        { x: 0, y: 0 }
    );

    // Количество запусков из параметров симуляции
    const { runs } = simulationParams;

    // Рендерим диаграмму на Konva Stage
    const renderDiagram = () => {
        if (!cells?.length) return null;

        // Рассчитываем размер канваса с учетом отступов
        const canvasWidth = (maxCoordinates.x + 1) * cellSize + padding * 2;
        const canvasHeight = (maxCoordinates.y + 1) * cellSize + padding * 2;

        return (
            <Stage
                width={stageWidth}
                height={stageHeight}
                onWheel={handleWheel}
                scaleX={scale}
                scaleY={scale}
                x={position.x}
                y={position.y}
                draggable
                onDragEnd={(e) => {
                    setPosition({
                        x: e.target.x(),
                        y: e.target.y(),
                    });
                }}
            >
                <Layer>
                    {/* Фон */}
                    <Rect
                        x={0}
                        y={0}
                        width={canvasWidth}
                        height={canvasHeight}
                        fill="#0f172a"
                    />

                    {/* Сетка */}
                    {Array.from({ length: maxCoordinates.y + 2 }).map(
                        (_, i) => (
                            <Line
                                key={`h-${i}`}
                                points={[
                                    padding,
                                    padding + i * cellSize,
                                    padding + (maxCoordinates.x + 1) * cellSize,
                                    padding + i * cellSize,
                                ]}
                                stroke="#1e293b"
                                strokeWidth={1}
                            />
                        )
                    )}
                    {Array.from({ length: maxCoordinates.x + 2 }).map(
                        (_, i) => (
                            <Line
                                key={`v-${i}`}
                                points={[
                                    padding + i * cellSize,
                                    padding,
                                    padding + i * cellSize,
                                    padding + (maxCoordinates.y + 1) * cellSize,
                                ]}
                                stroke="#1e293b"
                                strokeWidth={1}
                            />
                        )
                    )}

                    {/* Оси координат */}
                    <Line
                        points={[
                            padding - 10,
                            padding + maxCoordinates.y * cellSize,
                            padding + (maxCoordinates.x + 1) * cellSize + 10,
                            padding + maxCoordinates.y * cellSize,
                        ]}
                        stroke="#475569"
                        strokeWidth={2}
                    />
                    <Line
                        points={[
                            padding,
                            padding + maxCoordinates.y * cellSize + 10,
                            padding,
                            padding - 20,
                        ]}
                        stroke="#475569"
                        strokeWidth={2}
                    />

                    {/* Подписи к осям */}
                    <Text
                        x={padding - 15}
                        y={padding + maxCoordinates.y * cellSize + 15}
                        text="0"
                        fill="#94a3b8"
                        fontSize={12}
                    />
                    <Text
                        x={padding + (maxCoordinates.x + 1) * cellSize + 15}
                        y={padding + maxCoordinates.y * cellSize + 15}
                        text="X"
                        fill="#94a3b8"
                        fontSize={12}
                    />
                    <Text
                        x={padding - 15}
                        y={padding - 20}
                        text="Y"
                        fill="#94a3b8"
                        fontSize={12}
                    />

                    {/* Ячейки диаграммы */}
                    {cells.map((cell) => {
                        const { x, y, value } = cell;
                        const cellMargin = 1;
                        const actualCellSize = cellSize - 2 * cellMargin;

                        // Вычисляем насыщенность цвета в зависимости от значения ячейки и количества запусков
                        const colorIntensity = runs > 1 ? value : 1; // Если запусков несколько, используем value как интенсивность, иначе максимальная интенсивность

                        // Для нескольких запусков - усиливаем цвет с увеличением value
                        const baseColor = {
                            r: 20, // Базовый темно-голубой цвет
                            g: 184,
                            b: 214,
                        };

                        // Переход к более яркому цвету по мере увеличения значения
                        const brightColor = {
                            r: 6, // Ярко-голубой цвет
                            g: 214,
                            b: 255,
                        };

                        // Вычисляем результирующий цвет
                        const finalColor = {
                            r: Math.round(
                                baseColor.r +
                                    (brightColor.r - baseColor.r) *
                                        colorIntensity
                            ),
                            g: Math.round(
                                baseColor.g +
                                    (brightColor.g - baseColor.g) *
                                        colorIntensity
                            ),
                            b: Math.round(
                                baseColor.b +
                                    (brightColor.b - baseColor.b) *
                                        colorIntensity
                            ),
                        };

                        // Формируем строки цветов
                        const cellColor = `rgb(${finalColor.r}, ${finalColor.g}, ${finalColor.b})`;
                        const cellColorWithOpacity = (opacity: number) =>
                            `rgba(${finalColor.r}, ${finalColor.g}, ${finalColor.b}, ${opacity})`;

                        // Для каждой ячейки создаем отдельную группу
                        return (
                            <Group key={`cell-${x}-${y}`}>
                                {/* Свечение вокруг ячейки */}
                                <Rect
                                    x={padding + x * cellSize - cellSize * 0.1}
                                    y={padding + y * cellSize - cellSize * 0.1}
                                    width={cellSize * 1.2}
                                    height={cellSize * 1.2}
                                    fillRadialGradientStartPoint={{
                                        x: cellSize / 2,
                                        y: cellSize / 2,
                                    }}
                                    fillRadialGradientStartRadius={0}
                                    fillRadialGradientEndPoint={{
                                        x: cellSize / 2,
                                        y: cellSize / 2,
                                    }}
                                    fillRadialGradientEndRadius={cellSize}
                                    fillRadialGradientColorStops={[
                                        0,
                                        cellColorWithOpacity(value * 0.8),
                                        0.6,
                                        cellColorWithOpacity(value * 0.3),
                                        1,
                                        "rgba(6, 182, 212, 0)",
                                    ]}
                                    cornerRadius={3}
                                />

                                {/* Основная ячейка */}
                                <Rect
                                    x={padding + x * cellSize + cellMargin}
                                    y={padding + y * cellSize + cellMargin}
                                    width={actualCellSize}
                                    height={actualCellSize}
                                    fill={cellColor}
                                    opacity={0.5 + value * 0.5} // Прозрачность зависит от value
                                    cornerRadius={3}
                                    stroke={cellColorWithOpacity(0.8)}
                                    strokeWidth={1}
                                />

                                {/* Блик для 3D эффекта */}
                                <Line
                                    points={[
                                        padding + x * cellSize + cellMargin + 2,
                                        padding + y * cellSize + cellMargin + 2,
                                        padding +
                                            x * cellSize +
                                            cellMargin +
                                            10,
                                        padding + y * cellSize + cellMargin + 2,
                                        padding + x * cellSize + cellMargin + 2,
                                        padding +
                                            y * cellSize +
                                            cellMargin +
                                            10,
                                    ]}
                                    closed
                                    fill="rgba(255, 255, 255, 0.3)"
                                    opacity={value * 0.7} // Интенсивность блика зависит от value
                                />
                            </Group>
                        );
                    })}

                    {/* Метка с количеством запусков */}
                    {runs > 1 && (
                        <Text
                            x={canvasWidth - padding}
                            y={padding - 10}
                            text={`Запусков: ${runs}`}
                            fill="#94a3b8"
                            fontSize={14}
                            align="right"
                        />
                    )}

                    {/* Легенда для множественных запусков */}
                    {runs > 1 && (
                        <Group>
                            <Rect
                                x={padding}
                                y={padding - 30}
                                width={150}
                                height={20}
                                fill="rgba(15, 23, 42, 0.7)"
                                cornerRadius={4}
                            />
                            <Text
                                x={padding + 5}
                                y={padding - 25}
                                text="Яркость = частота появления"
                                fill="#94a3b8"
                                fontSize={12}
                            />
                        </Group>
                    )}
                </Layer>
            </Stage>
        );
    };

    return (
        <FlexBox
            direction="column"
            align="center"
            justify="center"
            className="visualization-container"
            style={{ width: "100%", height: "100%", overflow: "hidden" }}
        >
            {isLoading ? (
                <FlexBox
                    direction="column"
                    align="center"
                    justify="center"
                    gap={16}
                    style={{ height: "100%" }}
                >
                    <div className="loading-dots">
                        <div></div>
                        <div></div>
                        <div></div>
                    </div>
                    <p className="text-muted">Выполняется симуляция...</p>
                </FlexBox>
            ) : cells?.length ? (
                <div
                    ref={containerRef}
                    style={{
                        width: "100%",
                        height: "100%",
                        position: "relative",
                    }}
                >
                    {renderDiagram()}

                    {/* Подсказка по управлению */}
                    <div
                        style={{
                            position: "absolute",
                            bottom: "10px",
                            left: "10px",
                            backgroundColor: "rgba(15, 23, 42, 0.7)",
                            padding: "8px 12px",
                            borderRadius: "4px",
                            zIndex: 10,
                            fontSize: "14px",
                        }}
                    >
                        <p>Управление:</p>
                        <ul style={{ margin: "5px 0", paddingLeft: "20px" }}>
                            <li>Колесико мыши: масштабирование</li>
                            <li>Перетаскивание: перемещение</li>
                        </ul>
                    </div>
                </div>
            ) : (
                <FlexBox
                    direction="column"
                    align="center"
                    justify="center"
                    gap={16}
                    style={{ height: "100%" }}
                >
                    <p className="text-muted">
                        Настройте параметры и запустите симуляцию
                    </p>
                </FlexBox>
            )}
        </FlexBox>
    );
};

export default VisualizationCanvas2D;
