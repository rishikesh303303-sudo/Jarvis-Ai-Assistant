import { useState, useEffect, useRef } from "react";

const STATUS_CONFIG = {
  idle:      { label: "SLEEPING",    color: "#1e3a5f", ring: "#2563eb", pulse: false },
  active:    { label: "ONLINE",      color: "#1a3d2b", ring: "#22c55e", pulse: true  },
  listening: { label: "LISTENING",   color: "#3b1f5e", ring: "#a855f7", pulse: true  },
  thinking:  { label: "THINKING",    color: "#3b2a0a", ring: "#f59e0b", pulse: true  },
  speaking:  { label: "SPEAKING",    color: "#1e3040", ring: "#38bdf8", pulse: true  },
};

export default function JarvisDashboard() {
  const [status, setStatus] = useState("idle");
  const [text, setText] = useState("Say 'Hey Jarvis' to wake up");
  const [history, setHistory] = useState([]);
  const [connected, setConnected] = useState(false);
  const [particles, setParticles] = useState([]);
  const wsRef = useRef(null);
  const historyRef = useRef(null);
  const time = useCurrentTime();

  // Floating particles
  useEffect(() => {
    const pts = Array.from({ length: 40 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 3 + 1,
      speed: Math.random() * 20 + 15,
      delay: Math.random() * 10,
      opacity: Math.random() * 0.4 + 0.1,
    }));
    setParticles(pts);
  }, []);

  // WebSocket
  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket("ws://localhost:8000/ws");
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        console.log("Connected to Jarvis");
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          setStatus(data.status || "idle");
          setText(data.text || "");
          if (data.text && data.status !== "idle") {
            setHistory(prev => [
              { id: Date.now(), status: data.status, text: data.text, time: new Date().toLocaleTimeString() },
              ...prev.slice(0, 19)
            ]);
          }
        } catch {}
      };

      ws.onclose = () => {
        setConnected(false);
        setStatus("idle");
        setTimeout(connect, 3000);
      };

      ws.onerror = () => ws.close();
    };

    connect();
    return () => wsRef.current?.close();
  }, []);

  useEffect(() => {
    if (historyRef.current) historyRef.current.scrollTop = 0;
  }, [history]);

  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.idle;

  return (
    <div style={{
      minHeight: "100vh",
      background: "#030712",
      fontFamily: "'Orbitron', 'Courier New', monospace",
      color: "#e2e8f0",
      overflow: "hidden",
      position: "relative",
      display: "flex",
      flexDirection: "column",
    }}>
      {/* Google Font */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body { background: #030712; }

        @keyframes float {
          0%, 100% { transform: translateY(0px) translateX(0px); }
          33% { transform: translateY(-30px) translateX(10px); }
          66% { transform: translateY(10px) translateX(-15px); }
        }

        @keyframes pulse-ring {
          0%, 100% { box-shadow: 0 0 0 0 var(--ring), 0 0 40px var(--ring), 0 0 80px var(--ring); }
          50% { box-shadow: 0 0 0 20px transparent, 0 0 60px var(--ring), 0 0 120px var(--ring); }
        }

        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes spin-rev {
          from { transform: rotate(360deg); }
          to { transform: rotate(0deg); }
        }

        @keyframes scanline {
          0% { top: -5%; }
          100% { top: 105%; }
        }

        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateX(-10px); }
          to { opacity: 1; transform: translateX(0); }
        }

        @keyframes grid-move {
          0% { background-position: 0 0; }
          100% { background-position: 40px 40px; }
        }

        .history-item { animation: fadeIn 0.3s ease; }

        .orb-pulse {
          animation: pulse-ring 2s ease-in-out infinite;
        }

        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #0a0f1e; }
        ::-webkit-scrollbar-thumb { background: #1e40af; border-radius: 2px; }
      `}</style>

      {/* Animated Grid Background */}
      <div style={{
        position: "fixed", inset: 0, zIndex: 0,
        backgroundImage: `
          linear-gradient(rgba(37,99,235,0.08) 1px, transparent 1px),
          linear-gradient(90deg, rgba(37,99,235,0.08) 1px, transparent 1px)
        `,
        backgroundSize: "40px 40px",
        animation: "grid-move 8s linear infinite",
      }} />

      {/* Gradient Overlay */}
      <div style={{
        position: "fixed", inset: 0, zIndex: 1,
        background: `radial-gradient(ellipse at center, ${cfg.color}33 0%, #030712 70%)`,
        transition: "background 1s ease",
      }} />

      {/* Scanline */}
      <div style={{
        position: "fixed", left: 0, right: 0, height: "3px", zIndex: 2,
        background: "linear-gradient(90deg, transparent, rgba(37,99,235,0.6), transparent)",
        animation: "scanline 4s linear infinite",
        pointerEvents: "none",
      }} />

      {/* Floating Particles */}
      {particles.map(p => (
        <div key={p.id} style={{
          position: "fixed", zIndex: 1,
          left: `${p.x}%`, top: `${p.y}%`,
          width: `${p.size}px`, height: `${p.size}px`,
          borderRadius: "50%",
          background: cfg.ring,
          opacity: p.opacity,
          animation: `float ${p.speed}s ease-in-out ${p.delay}s infinite`,
          transition: "background 1s ease",
        }} />
      ))}

      {/* Main Content */}
      <div style={{
        position: "relative", zIndex: 10,
        display: "flex", flexDirection: "column",
        alignItems: "center", minHeight: "100vh",
        padding: "20px",
      }}>

        {/* Header */}
        <div style={{
          width: "100%", display: "flex",
          justifyContent: "space-between", alignItems: "center",
          marginBottom: "30px",
        }}>
          <div style={{ fontSize: "11px", color: "#4b5563", fontFamily: "'Share Tech Mono', monospace" }}>
            SYS: {connected ? <span style={{color:"#22c55e"}}>ONLINE</span> : <span style={{color:"#ef4444"}}>OFFLINE</span>}
          </div>
          <div style={{
            fontSize: "28px", fontWeight: "900", letterSpacing: "8px",
            color: cfg.ring, textShadow: `0 0 20px ${cfg.ring}`,
            transition: "color 1s, text-shadow 1s",
          }}>
            J.A.R.V.I.S
          </div>
          <div style={{ fontSize: "11px", color: "#4b5563", fontFamily: "'Share Tech Mono', monospace" }}>
            {time}
          </div>
        </div>

        {/* Central Orb */}
        <div style={{ position: "relative", width: "280px", height: "280px", marginBottom: "40px" }}>

          {/* Outer spinning ring */}
          <div style={{
            position: "absolute", inset: "-20px",
            border: `1px solid ${cfg.ring}44`,
            borderRadius: "50%",
            borderTopColor: cfg.ring,
            animation: "spin-slow 6s linear infinite",
            transition: "border-color 1s",
          }} />

          {/* Middle spinning ring */}
          <div style={{
            position: "absolute", inset: "-5px",
            border: `1px solid ${cfg.ring}33`,
            borderRadius: "50%",
            borderBottomColor: cfg.ring,
            animation: "spin-rev 4s linear infinite",
            transition: "border-color 1s",
          }} />

          {/* Inner ring */}
          <div style={{
            position: "absolute", inset: "10px",
            border: `1px solid ${cfg.ring}22`,
            borderRadius: "50%",
            borderLeftColor: cfg.ring,
            animation: "spin-slow 8s linear infinite",
            transition: "border-color 1s",
          }} />

          {/* Main Orb */}
          <div
            className={cfg.pulse ? "orb-pulse" : ""}
            style={{
              "--ring": cfg.ring,
              position: "absolute", inset: "20px",
              borderRadius: "50%",
              background: `radial-gradient(circle at 35% 35%, ${cfg.ring}44, ${cfg.color}cc, #030712)`,
              border: `2px solid ${cfg.ring}88`,
              display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              transition: "background 1s, border-color 1s",
              cursor: "default",
            }}
          >
            {/* Arc Reactor Style Center */}
            <div style={{
              width: "60px", height: "60px",
              borderRadius: "50%",
              border: `3px solid ${cfg.ring}`,
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: `0 0 20px ${cfg.ring}, inset 0 0 20px ${cfg.ring}33`,
              transition: "border-color 1s, box-shadow 1s",
              marginBottom: "8px",
            }}>
              <div style={{
                width: "24px", height: "24px", borderRadius: "50%",
                background: cfg.ring,
                boxShadow: `0 0 15px ${cfg.ring}`,
                transition: "background 1s, box-shadow 1s",
              }} />
            </div>

            <div style={{
              fontSize: "10px", letterSpacing: "4px",
              color: cfg.ring, fontWeight: "700",
              textShadow: `0 0 10px ${cfg.ring}`,
              transition: "color 1s",
            }}>
              {cfg.label}
            </div>
          </div>
        </div>

        {/* Status Text */}
        <div style={{
          maxWidth: "600px", width: "100%", textAlign: "center",
          marginBottom: "30px",
          background: "#0a0f1e88",
          border: `1px solid ${cfg.ring}44`,
          borderRadius: "8px", padding: "20px",
          backdropFilter: "blur(10px)",
          transition: "border-color 1s",
        }}>
          <div style={{
            fontSize: "13px", letterSpacing: "2px",
            color: cfg.ring, marginBottom: "8px", opacity: 0.7,
            fontFamily: "'Share Tech Mono', monospace",
          }}>
            {cfg.label} {status === "listening" && <span style={{animation:"blink 1s infinite", display:"inline-block"}}>▮</span>}
          </div>
          <div style={{
            fontSize: "16px", lineHeight: "1.6",
            color: "#e2e8f0", fontFamily: "'Share Tech Mono', monospace",
            minHeight: "24px",
          }}>
            {text || "—"}
          </div>
        </div>

        {/* Stats Bar */}
        <div style={{
          display: "flex", gap: "20px", marginBottom: "30px",
          flexWrap: "wrap", justifyContent: "center",
        }}>
          {[
            { label: "VOICE ENGINE", val: "ACTIVE" },
            { label: "AI BRAIN", val: "GEMINI" },
            { label: "CITY", val: "BHOPAL" },
          ].map(s => (
            <div key={s.label} style={{
              background: "#0a0f1e",
              border: `1px solid ${cfg.ring}33`,
              borderRadius: "6px", padding: "8px 16px",
              textAlign: "center", minWidth: "120px",
              transition: "border-color 1s",
            }}>
              <div style={{ fontSize: "9px", color: "#4b5563", letterSpacing: "2px", marginBottom: "4px" }}>
                {s.label}
              </div>
              <div style={{ fontSize: "12px", color: cfg.ring, fontWeight: "700", transition: "color 1s" }}>
                {s.val}
              </div>
            </div>
          ))}
        </div>

        {/* Command History */}
        <div style={{
          maxWidth: "700px", width: "100%",
          background: "#0a0f1e88",
          border: "1px solid #1e3a5f",
          borderRadius: "8px", overflow: "hidden",
          backdropFilter: "blur(10px)",
        }}>
          <div style={{
            padding: "12px 16px",
            borderBottom: "1px solid #1e3a5f",
            fontSize: "10px", letterSpacing: "3px", color: "#4b5563",
          }}>
            COMMAND LOG
          </div>
          <div ref={historyRef} style={{
            maxHeight: "220px", overflowY: "auto", padding: "8px",
          }}>
            {history.length === 0 ? (
              <div style={{
                padding: "20px", textAlign: "center",
                color: "#374151", fontSize: "12px",
                fontFamily: "'Share Tech Mono', monospace",
              }}>
                No commands yet. Say 'Hey Jarvis' to begin.
              </div>
            ) : history.map(h => (
              <div key={h.id} className="history-item" style={{
                display: "flex", gap: "12px", alignItems: "flex-start",
                padding: "8px", borderRadius: "4px",
                marginBottom: "4px",
                background: "#0d1424",
                borderLeft: `2px solid ${STATUS_CONFIG[h.status]?.ring || "#374151"}`,
              }}>
                <div style={{
                  fontSize: "9px", color: "#4b5563", whiteSpace: "nowrap",
                  fontFamily: "'Share Tech Mono', monospace", paddingTop: "2px",
                }}>
                  {h.time}
                </div>
                <div style={{
                  fontSize: "12px", color: "#94a3b8",
                  fontFamily: "'Share Tech Mono', monospace", lineHeight: "1.5",
                }}>
                  {h.text}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div style={{
          marginTop: "20px", fontSize: "9px", color: "#1f2937",
          letterSpacing: "3px", textAlign: "center",
        }}>
          STARK INDUSTRIES — PERSONAL AI ASSISTANT — v2.0
        </div>
      </div>
    </div>
  );
}

function useCurrentTime() {
  const [time, setTime] = useState(new Date().toLocaleTimeString());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(t);
  }, []);
  return time;
}