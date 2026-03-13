import { useRef, useEffect, useState, useCallback, ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './GooeyNav.css';

interface NavItem {
  label: string;
  href: string;
  icon?: ReactNode;
  onClick?: () => void;
}

interface GooeyNavProps {
  items: NavItem[];
  animationTime?: number;
  particleCount?: number;
  particleDistances?: [number, number];
  particleR?: number;
  timeVariance?: number;
  colors?: number[];
}

const GooeyNav = ({
  items,
  animationTime = 600,
  particleCount = 15,
  particleDistances = [90, 10],
  particleR = 100,
  timeVariance = 300,
  colors = [1, 2, 3, 1, 2, 3, 1, 4],
}: GooeyNavProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const navRef = useRef<HTMLUListElement>(null);
  const filterRef = useRef<HTMLSpanElement>(null);
  const textRef = useRef<HTMLSpanElement>(null);
  const navigate = useNavigate();
  const location = useLocation();

  const activeIndex = items.findIndex(
    (item) =>
      location.pathname === item.href ||
      (item.href !== '/dashboard' && location.pathname.startsWith(item.href))
  );
  const [visualIndex, setVisualIndex] = useState(activeIndex >= 0 ? activeIndex : 0);

  const noise = (n = 1) => n / 2 - Math.random() * n;

  const getXY = useCallback(
    (distance: number, pointIndex: number, totalPoints: number): [number, number] => {
      const angle = ((360 + noise(8)) / totalPoints) * pointIndex * (Math.PI / 180);
      return [distance * Math.cos(angle), distance * Math.sin(angle)];
    },
    []
  );

  const createParticle = useCallback(
    (i: number, t: number, d: [number, number], r: number) => {
      const rotate = noise(r / 10);
      return {
        start: getXY(d[0], particleCount - i, particleCount),
        end: getXY(d[1] + noise(7), particleCount - i, particleCount),
        time: t,
        scale: 1 + noise(0.2),
        color: colors[Math.floor(Math.random() * colors.length)],
        rotate: rotate > 0 ? (rotate + r / 20) * 10 : (rotate - r / 20) * 10,
      };
    },
    [getXY, particleCount, colors]
  );

  const makeParticles = useCallback(
    (element: HTMLSpanElement) => {
      const d = particleDistances;
      const r = particleR;
      const bubbleTime = animationTime * 2 + timeVariance;
      element.style.setProperty('--time', `${bubbleTime}ms`);

      for (let i = 0; i < particleCount; i++) {
        const t = animationTime * 2 + noise(timeVariance * 2);
        const p = createParticle(i, t, d, r);
        element.classList.remove('active');

        setTimeout(() => {
          const particle = document.createElement('span');
          const point = document.createElement('span');
          particle.classList.add('particle');
          particle.style.setProperty('--start-x', `${p.start[0]}px`);
          particle.style.setProperty('--start-y', `${p.start[1]}px`);
          particle.style.setProperty('--end-x', `${p.end[0]}px`);
          particle.style.setProperty('--end-y', `${p.end[1]}px`);
          particle.style.setProperty('--time', `${p.time}ms`);
          particle.style.setProperty('--scale', `${p.scale}`);
          particle.style.setProperty('--color', `var(--color-${p.color}, #6366f1)`);
          particle.style.setProperty('--rotate', `${p.rotate}deg`);
          point.classList.add('point');
          particle.appendChild(point);
          element.appendChild(particle);
          requestAnimationFrame(() => element.classList.add('active'));
          setTimeout(() => {
            try { element.removeChild(particle); } catch { /* removed already */ }
          }, t);
        }, 30);
      }
    },
    [animationTime, particleCount, particleDistances, particleR, timeVariance, createParticle]
  );

  const updateEffectPosition = useCallback((element: HTMLLIElement) => {
    if (!containerRef.current || !filterRef.current || !textRef.current) return;
    const containerRect = containerRef.current.getBoundingClientRect();
    const pos = element.getBoundingClientRect();
    const styles = {
      left: `${pos.x - containerRect.x}px`,
      top: `${pos.y - containerRect.y}px`,
      width: `${pos.width}px`,
      height: `${pos.height}px`,
    };
    Object.assign(filterRef.current.style, styles);
    Object.assign(textRef.current.style, styles);
  }, []);

  const handleClick = useCallback(
    (index: number, item: NavItem) => {
      if (visualIndex === index) return;

      const liEl = navRef.current?.querySelectorAll('li')[index] as HTMLLIElement | undefined;
      if (!liEl) return;

      setVisualIndex(index);
      updateEffectPosition(liEl);

      if (filterRef.current) {
        filterRef.current.querySelectorAll('.particle').forEach((p) =>
          filterRef.current!.removeChild(p)
        );
        textRef.current?.classList.remove('active');
        void textRef.current?.offsetWidth;
        textRef.current?.classList.add('active');
        makeParticles(filterRef.current);
      }

      // React Router navigation
      navigate(item.href);
      item.onClick?.();
    },
    [visualIndex, updateEffectPosition, makeParticles, navigate]
  );

  // Sync visual index when route changes externally
  useEffect(() => {
    const idx = items.findIndex(
      (item) =>
        location.pathname === item.href ||
        (item.href !== '/dashboard' && location.pathname.startsWith(item.href))
    );
    if (idx >= 0 && idx !== visualIndex) setVisualIndex(idx);
  }, [location.pathname, items]);

  // Position the effect on the active item after mount / resize
  useEffect(() => {
    if (!navRef.current || !containerRef.current) return;
    const activeLi = navRef.current.querySelectorAll('li')[visualIndex] as HTMLLIElement | undefined;
    if (activeLi) {
      updateEffectPosition(activeLi);
      textRef.current?.classList.add('active');
    }

    const ro = new ResizeObserver(() => {
      const li = navRef.current?.querySelectorAll('li')[visualIndex] as HTMLLIElement | undefined;
      if (li) updateEffectPosition(li);
    });
    ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, [visualIndex, updateEffectPosition]);

  return (
    <div className="gooey-nav-container" ref={containerRef}>
      <nav>
        <ul ref={navRef}>
          {items.map((item, index) => (
            <li
              key={item.href}
              className={visualIndex === index ? 'active' : ''}
              onClick={() => handleClick(index, item)}
            >
              <a
                href={item.href}
                onClick={(e) => e.preventDefault()}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleClick(index, item);
                  }
                }}
              >
                {item.icon && <span className="shrink-0">{item.icon}</span>}
                {item.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
      <span className="effect filter" ref={filterRef} />
      <span className="effect text" ref={textRef} />
    </div>
  );
};

export default GooeyNav;
