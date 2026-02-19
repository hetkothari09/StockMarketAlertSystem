import React, { useEffect, useRef } from 'react';
import { createChart, HistogramSeries } from 'lightweight-charts';

const ChartModal = ({ symbol, onClose }) => {
    const chartContainerRef = useRef();

    useEffect(() => {
        if (!symbol) return;

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { color: '#020617' },
                textColor: '#d1d5db',
            },
            grid: {
                vertLines: { color: '#1f2937' },
                horzLines: { color: '#1f2937' },
            },
            width: chartContainerRef.current.clientWidth,
            height: 400,
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
            },
        });

        const volumeSeries = chart.addSeries(HistogramSeries, {
            color: '#3b82f6',
            priceFormat: { type: 'volume' },
        });

        // Fetch historical data
        fetch(`http://${window.location.hostname}:7000/historical/${symbol}`)
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) {
                    volumeSeries.setData(data);
                    chart.timeScale().fitContent();
                }
            })
            .catch(err => console.error("Failed to load history", err));

        const handleResize = () => {
            chart.applyOptions({ width: chartContainerRef.current.clientWidth });
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [symbol]);

    if (!symbol) return null;

    return (
        <div style={{
            position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.8)',
            display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
        }}>
            <div style={{
                width: '80%', height: '500px', backgroundColor: '#020617',
                border: '1px solid #1f2937', borderRadius: '8px', display: 'flex', flexDirection: 'column'
            }}>
                <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{symbol} – Volume Analysis</span>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '18px' }}>✕</button>
                </div>
                <div ref={chartContainerRef} style={{ flex: 1, width: '100%' }} />
            </div>
        </div>
    );
};

export default ChartModal;
