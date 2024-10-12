import { List, ListItem } from '@tremor/react';
import { BaseCard } from '../../../components/base-comps';
import { ModelData } from '@/app/utils/definitions';
import {
  RiArrowUpWideLine,
  RiBattery2ChargeLine,
  RiCompassLine,
  RiHome4Line,
  RiLightbulbFlashLine,
  RiSunLine
} from '@remixicon/react';
import { fetchModels } from '@/app/utils/helpers';

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


export async function ModelSummary({model_id}: {model_id: string}) {

  const models: ModelData[] = await fetchModels();
  const model: ModelData | undefined = models.find((model) => model.model_id === model_id);
  if (!model) {
      return <div>Model not found</div>;
  }

  return (
    <div>
      <BaseCard title="Model Summary">
      <div className="flex flex-row justify-between w-full">
        <List className="mt-2 px-4">
          <ListItem key={model.location}>
            <RiHome4Line />
            <span>{ model.location }</span>
          </ListItem>
          <ListItem key={model.roof_incl}>
            <RiArrowUpWideLine />
            <span>{ degreeFormatter(model.roof_incl) }</span>
          </ListItem>
          <ListItem key={model.roof_azimuth}>
            <RiCompassLine />
            <span>{ azimuthFormatter(model.roof_azimuth) }</span>
          </ListItem>
        </List>
        <List className="mt-2 px-4">
          <ListItem key={model.electr_cons}>
            <RiLightbulbFlashLine />
            <span>{ valueFormatter(model.electr_cons, "kWh")}</span>
          </ListItem>
          <ListItem key={model.peak_power}>
            <RiSunLine />
            <span>{ valueFormatter(model.peak_power, "kWp")}</span>
          </ListItem>
          <ListItem key={model.battery_cap}>
            <RiBattery2ChargeLine />
            <span>{ valueFormatter(model.battery_cap, "kWh")}</span>
          </ListItem>
        </List>
      </div>
      </BaseCard>
    </div>
  );
}
