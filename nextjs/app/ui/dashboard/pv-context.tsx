import React from 'react';
import { SimEvaluation } from '@/app/lib/definitions';

const SimDataContext = React.createContext<SimEvaluation | null>(null);

export default SimDataContext;
