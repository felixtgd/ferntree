import { List, ListItem } from '@tremor/react';
import { BaseCard } from './base-comps';
import {
  RiArrowUpWideLine,
  RiBattery2ChargeLine,
  RiCompassLine,
  RiHome4Line,
  RiLightbulbFlashLine,
  RiSunLine
} from '@remixicon/react';

const valueFormatter = (value: number, unit: string): string => {
  return `${value} ${unit}`;
}

const degreeFormatter = (value: number): string => {
  return `${value}°`;
}

const azimuthFormatter = (degree: number): string => {
  const directionMap: Record<string, string> = {
    "0": "South",
    "45": "South-West",
    "90": "West",
    "135": "North-West",
    "180": "North",
    "-45": "South-East",
    "-90": "East",
    "-135": "North-East",
  };

  return directionMap[degree.toString()] || "Unknown Orientation";
};


export async function ModelSummary({modelId}: {modelId: string}) {

  // const simResults : SimEvaluation = await fetchSimResults(modelId);
  // const kpis : SimFinancialKPIs = simResults.financial_analysis.kpis;

  const model_summary = {
    modelId: modelId, // temp
    location: 'Aarau',
    electr_cons: 6000,
    roof_incl: 0,
    roof_azimuth: 0,
    peak_power: 10,
    battery_cap: 10,
  }

  return (
    <div>
      <BaseCard title="Model Summary">
      <div className="flex flex-row justify-between w-full">
        <List className="mt-2 px-6">
          <ListItem key={model_summary.location}>
            <RiHome4Line />
            <span>{ model_summary.location }</span>
          </ListItem>
          <ListItem key={model_summary.roof_incl}>
            <RiArrowUpWideLine />
            <span>{ degreeFormatter(model_summary.roof_incl) }</span>
          </ListItem>
          <ListItem key={model_summary.roof_azimuth}>
            <RiCompassLine />
            <span>{ azimuthFormatter(model_summary.roof_azimuth) }</span>
          </ListItem>
        </List>
        <List className="mt-2 px-6">
          <ListItem key={model_summary.electr_cons}>
            <RiLightbulbFlashLine />
            <span>{ valueFormatter(model_summary.electr_cons, "kWh")}</span>
          </ListItem>
          <ListItem key={model_summary.peak_power}>
            <RiSunLine />
            <span>{ valueFormatter(model_summary.peak_power, "kWp")}</span>
          </ListItem>
          <ListItem key={model_summary.battery_cap}>
            <RiBattery2ChargeLine />
            <span>{ valueFormatter(model_summary.battery_cap, "kWh")}</span>
          </ListItem>
        </List>
      </div>
      </BaseCard>
    </div>
  );
}
