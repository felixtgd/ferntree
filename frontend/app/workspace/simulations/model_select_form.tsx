'use client';

import { GoToFinButton, RunSimButton, ViewSimButton } from "@/app/components/buttons";
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
import Link from "next/link";

export function ModelSelectForm({models}: {models: ModelData[]}) {

    const [modelData, setModelData] = useState(models[0]);

    // If models is empty list, return div with link to models page
    if (models.length === 0) {
        return (
            <div className="flex flex-col w-full items-center">
                <h2 className="w-full text-center mb-4">
                    Please <Link href="/workspace/models" className="text-blue-500">create a model</Link> first.
                </h2>
            </div>
        );
    }

    return (
        <div className="flex flex-col w-full items-center">
            <h2 className="w-full text-center mb-4">
                Model
            </h2>

            <div className="mb-4 w-full relative">
                <Select
                        id="model"
                        name="model"
                        icon={RiShapesLine}
                        onValueChange={
                            (value: string) => {
                                const selectedModel = models.find((model) => model.model_id === value) ?? models[0];
                                setModelData(selectedModel);
                            }
                        }
                        value={modelData.model_id as string}
                    >
                        {models.map((modelData) => (
                            <SelectItem key={modelData.model_id as string} value={modelData.model_id as string}>{modelData.model_name}</SelectItem>
                        ))}
                    </Select>
            </div>

            <div className="flex flex-col w-full items-center">
                <div className="flex flex-col md:flex-row w-full">
                    <List className="p-2 w-full">

                        <ListItem key="location">
                            <span className="flex items-center">
                                <RiHome4Line className="mr-2" /> Location
                            </span>
                            <span>{modelData.location}</span>
                        </ListItem>

                        <ListItem key="roof_incl">
                            <span className="flex items-center">
                                <RiArrowUpWideLine className="mr-2" /> Roof inclination
                            </span>
                            <span>{modelData.roof_incl}°</span>
                        </ListItem>

                        <ListItem key="roof_azimuth">
                            <span className="flex items-center">
                                <RiCompassLine className="mr-2" /> Roof orientation
                            </span>
                            <span>{modelData.roof_azimuth}°</span>
                        </ListItem>

                        <ListItem key="electr_cons">
                            <span className="flex items-center">
                                <RiLightbulbFlashLine className="mr-2" /> Consumption
                            </span>
                            <span>{modelData.electr_cons} kWh</span>
                        </ListItem>

                        <ListItem key="peak_power">
                            <span className="flex items-center">
                                <RiSunLine className="mr-2" /> PV peak power
                            </span>
                            <span>{modelData.peak_power} kWp</span>
                        </ListItem>

                        <ListItem key="battery_cap">
                            <span className="flex items-center">
                                <RiBattery2ChargeLine className="mr-2" /> Battery capacity
                            </span>
                            <span>{modelData.battery_cap} kWh</span>
                        </ListItem>

                    </List>
                </div>
            </div>

            <div className="flex flex-row justify-center m-2">
                {modelData.model_id && (
                    modelData.sim_id
                        ?
                            <>
                                <ViewSimButton model_id={modelData.model_id} />
                                <GoToFinButton model_id={modelData.model_id} />
                            </>
                        : <RunSimButton model_id={modelData.model_id} />
                    )
                }
            </div>

        </div>
    );
}
