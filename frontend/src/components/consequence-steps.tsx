"use client";

import { useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui";

export type ConsequenceStep = {
  id: string;
  label: string;
  title: string;
  summary: string;
  detail: ReactNode;
};

export default function ConsequenceSteps({ steps, identity }: { steps: ConsequenceStep[]; identity: string }) {
  const [active, setActive] = useState(0);
  const buttons = useRef<Array<HTMLButtonElement | null>>([]);
  useEffect(() => { setActive(0); }, [identity]);

  function select(index: number, focus = false) {
    const next = Math.max(0, Math.min(steps.length - 1, index));
    setActive(next);
    if (focus) window.requestAnimationFrame(() => buttons.current[next]?.focus());
  }

  function navigate(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    const target = event.key === "ArrowRight" ? index + 1
      : event.key === "ArrowLeft" ? index - 1
      : event.key === "Home" ? 0
      : event.key === "End" ? steps.length - 1 : null;
    if (target == null) return;
    event.preventDefault();
    select(target, true);
  }

  return <>
    <ol className="consequence-steps" aria-label="Consequence path steps">
      {steps.map((step, index) => <li className="consequence-step" data-active={index === active} key={step.id}>
        <button ref={element => { buttons.current[index] = element; }} type="button" aria-current={index === active ? "step" : undefined} aria-controls="consequence-step-detail" tabIndex={index === active ? 0 : -1} onClick={() => select(index)} onKeyDown={event => navigate(event, index)}>
          <small>{index + 1} · {step.label}</small>
          <strong>{step.title}</strong>
          <p>{step.summary}</p>
        </button>
      </li>)}
    </ol>
    <div id="consequence-step-detail" className="consequence-detail" role="region" aria-live="polite" aria-label={`${steps[active].label} detail`}>
      <h3>{steps[active].title}</h3>
      {steps[active].detail}
    </div>
    <div className="consequence-controls">
      <span className="helper">Use Left/Right, Home and End on the steps.</span>
      <div><Button disabled={active === 0} onClick={() => select(active - 1, true)}><ArrowLeft size={13} /> Previous</Button><Button disabled={active === steps.length - 1} onClick={() => select(active + 1, true)}>Next <ArrowRight size={13} /></Button></div>
    </div>
  </>;
}
