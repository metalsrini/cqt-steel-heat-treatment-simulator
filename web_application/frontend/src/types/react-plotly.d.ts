declare module 'plotly.js' {
  export interface PlotData {
    x?: any[];
    y?: any[];
    z?: any[];
    type?: string;
    mode?: string;
    name?: string;
    line?: any;
    marker?: any;
    text?: any;
    hovertemplate?: string;
    showlegend?: boolean;
    [key: string]: any;
  }

  export interface Layout {
    title?: string | { text: string; [key: string]: any };
    xaxis?: any;
    yaxis?: any;
    width?: number;
    height?: number;
    margin?: any;
    showlegend?: boolean;
    legend?: any;
    font?: any;
    plot_bgcolor?: string;
    paper_bgcolor?: string;
    [key: string]: any;
  }

  export interface Config {
    displayModeBar?: boolean;
    displaylogo?: boolean;
    modeBarButtonsToRemove?: string[];
    responsive?: boolean;
    [key: string]: any;
  }

  export interface PlotMouseEvent {
    points: any[];
    event: MouseEvent;
  }

  export interface PlotRelayoutEvent {
    [key: string]: any;
  }

  export interface PlotSelectionEvent {
    points: any[];
    [key: string]: any;
  }

  export type Data = PlotData;
}

declare module 'react-plotly.js' {
  import { Component } from 'react';
  import { PlotData, Layout, Config, PlotMouseEvent, PlotRelayoutEvent, PlotSelectionEvent } from 'plotly.js';

  export interface PlotParams {
    data: Partial<PlotData>[];
    layout?: Partial<Layout>;
    config?: Partial<Config>;
    frames?: any[];
    revision?: number;
    onInitialized?: (figure: Readonly<{ data: PlotData[]; layout: Layout }>, graphDiv: HTMLElement) => void;
    onUpdate?: (figure: Readonly<{ data: PlotData[]; layout: Layout }>, graphDiv: HTMLElement) => void;
    onPurge?: (figure: Readonly<{ data: PlotData[]; layout: Layout }>, graphDiv: HTMLElement) => void;
    onError?: (err: Error) => void;
    onBeforeExport?: () => void;
    onAfterExport?: () => void;
    onAnimatingFrame?: (frameData: any) => void;
    onAnimationInterrupt?: () => void;
    onAutoSize?: () => void;
    onClick?: (event: PlotMouseEvent) => void;
    onClickAnnotation?: (event: PlotMouseEvent) => void;
    onDoubleClick?: () => void;
    onHover?: (event: PlotMouseEvent) => void;
    onUnhover?: (event: PlotMouseEvent) => void;
    onSelected?: (event: PlotSelectionEvent) => void;
    onSelecting?: (event: PlotSelectionEvent) => void;
    onRestyle?: (eventData: any[]) => void;
    onRedraw?: () => void;
    onRelayout?: (event: PlotRelayoutEvent) => void;
    onRelayouting?: (event: PlotRelayoutEvent) => void;
    onAfterPlot?: () => void;
    onBeforePlot?: () => void;
    onAnimated?: () => void;
    onLegendClick?: (event: any) => boolean;
    onLegendDoubleClick?: (event: any) => boolean;
    onSliderChange?: (event: any) => void;
    onSliderEnd?: (event: any) => void;
    onSliderStart?: (event: any) => void;
    onTransitioning?: () => void;
    onTransitionInterrupt?: () => void;
    onWebGlContextLost?: () => void;
    divId?: string;
    className?: string;
    style?: React.CSSProperties;
    debug?: boolean;
    useResizeHandler?: boolean;
  }

  export default class Plot extends Component<PlotParams> {}
}