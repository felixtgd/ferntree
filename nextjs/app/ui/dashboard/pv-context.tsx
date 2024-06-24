import { createContext } from 'react';
import { SimEvaluation } from '@/app/lib/definitions';

const SimDataContext = createContext<SimEvaluation | null>(null);

export default SimDataContext;
