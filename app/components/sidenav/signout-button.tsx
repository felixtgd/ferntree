'use client'

import { Button } from '@tremor/react';
import { RiShutDownLine } from '@remixicon/react';

export default function SignoutButton() {
  return (
    <Button
    variant='primary'
    icon={RiShutDownLine}
    className='flex h-[48px] flex-grow w-full items-center justify-start gap-2'
    >
      Sign Out
    </Button>
  );
}
