import { useEffect, useState } from 'react';

type NavigatorWithMemory = Navigator & { deviceMemory?: number };

export function useDeviceCapability() {
  const [canRender3D, setCanRender3D] = useState(true);

  useEffect(() => {
    const nav = navigator as NavigatorWithMemory;
    const lowCpu = typeof nav.hardwareConcurrency === 'number' && nav.hardwareConcurrency <= 4;
    const lowMemory = typeof nav.deviceMemory === 'number' && nav.deviceMemory <= 2;
    setCanRender3D(!(lowCpu || lowMemory));
  }, []);

  return { canRender3D };
}
