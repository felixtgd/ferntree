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
import type { ModelSummary } from '@/app/data/definitions';
import { fetchModelSummary } from './actions';

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

  const modelSummary : ModelSummary = await fetchModelSummary(modelId);

  return (
    <div>
      <BaseCard title="Model Summary">
      <div className="flex flex-row justify-between w-full h-full">
        <List className="mt-2 px-6">
          <ListItem key={modelSummary.location}>
            <RiHome4Line />
            <span>{ modelSummary.location }</span>
          </ListItem>
          <ListItem key={modelSummary.roof_incl}>
            <RiArrowUpWideLine />
            <span>{ degreeFormatter(modelSummary.roof_incl) }</span>
          </ListItem>
          <ListItem key={modelSummary.roof_azimuth}>
            <RiCompassLine />
            <span>{ azimuthFormatter(modelSummary.roof_azimuth) }</span>
          </ListItem>
        </List>
        <List className="mt-2 px-6">
          <ListItem key={modelSummary.electr_cons}>
            <RiLightbulbFlashLine />
            <span>{ valueFormatter(modelSummary.electr_cons, "kWh/a")}</span>
          </ListItem>
          <ListItem key={modelSummary.peak_power}>
            <RiSunLine />
            <span>{ valueFormatter(modelSummary.peak_power, "kWp")}</span>
          </ListItem>
          <ListItem key={modelSummary.battery_cap}>
            <RiBattery2ChargeLine />
            <span>{ valueFormatter(modelSummary.battery_cap, "kWh")}</span>
          </ListItem>
        </List>
      </div>
      </BaseCard>
    </div>
  );
}
