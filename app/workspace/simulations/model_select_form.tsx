'use client';

import { RunButton, ViewButton } from "@/app/components/buttons";
import { Select, SelectItem, List, ListItem } from "@tremor/react";
import { RiShapesLine } from "@remixicon/react";
import { ModelData } from "@/app/utils/definitions";
import { useState } from "react";
import {
  RiArrowUpWideLine,
  RiBattery2ChargeLine,
  RiCompassLine,
  RiHome4Line,
  RiLightbulbFlashLine,
  RiSunLine
} from '@remixicon/react';

export function ModelSelectForm({models}: {models: ModelData[]}) {

    const [modelData, setModelData] = useState(models[0]);

    return (
        <div className="flex flex-col w-full items-center">
            <form className="w-full">
                <h2 className="w-full text-center mb-4">
                    Select a model
                </h2>

                <div className="mb-4 w-full relative">
                    <Select
                        id="model"
                        name="model"
                        icon={RiShapesLine}
                        onValueChange={
                            (value: string) => {
                                const selectedModel = models.find((model) => model.model_id === value) as ModelData;
                                setModelData(selectedModel);
                            }
                        }
                        value = {modelData.model_id as string}
                    >
                        {models.map((modelData, index) => (
                            <SelectItem key={index} value={modelData.model_id as string}>{modelData.model_name}</SelectItem>
                        ))}
                    </Select>
                </div>
            </form>

            <div className="flex flex-col w-full items-center">
                <div className="flex flex-col md:flex-row w-full">
                    <List className="p-2 w-full">

                        <ListItem key="location">
                            <span className="flex items-center">
                                <RiHome4Line className="mr-2" />
                            </span>
                            <span>{modelData.location}</span>
                        </ListItem>

                        <ListItem key="roof_incl">
                            <span className="flex items-center">
                                <RiArrowUpWideLine className="mr-2" />
                            </span>
                            <span>{modelData.roof_incl}°</span>
                        </ListItem>

                        <ListItem key="roof_azimuth">
                            <span className="flex items-center">
                                <RiCompassLine className="mr-2" />
                            </span>
                            <span>{modelData.roof_azimuth}°</span>
                        </ListItem>

                        <ListItem key="electr_cons">
                            <span className="flex items-center">
                                <RiLightbulbFlashLine className="mr-2" />
                            </span>
                            <span>{modelData.electr_cons} kWh</span>
                        </ListItem>

                        <ListItem key="peak_power">
                            <span className="flex items-center">
                                <RiSunLine className="mr-2" />
                            </span>
                            <span>{modelData.peak_power} kWp</span>
                        </ListItem>

                        <ListItem key="roof_azimuth">
                            <span className="flex items-center">
                                <RiBattery2ChargeLine className="mr-2" />
                            </span>
                            <span>{modelData.battery_cap} kWh</span>
                        </ListItem>

                    </List>
                </div>
            </div>

            <div className="flex flex-col justify-center m-2">
                {modelData.model_id && (
                    modelData.sim_id
                        ? <ViewButton type="model" model_id={modelData.model_id} />
                        : <RunButton type="model" model_id={modelData.model_id} />
                    )
                }
            </div>

        </div>
    );
}
