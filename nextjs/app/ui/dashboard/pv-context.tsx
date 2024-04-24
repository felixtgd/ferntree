import React from 'react';
import { PvData } from '@/app/lib/definitions';

const PvDataContext = React.createContext<PvData | null>(null);

export default PvDataContext;
