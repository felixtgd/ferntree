'use client';

import { GoToFinButton, RunSimButton, ViewSimButton } from "@/app/components/buttons";
import { Select, SelectItem, List, ListItem } from "@tremor/react";
import { RiShapesLine } from "@remixicon/react";
import { ModelData } from "@/app/utils/definitions";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import {
  RiArrowUpWideLine,
  RiBattery2ChargeLine,
  RiCompassLine,
  RiHome4Line,
  RiLightbulbFlashLine,
  RiSunLine
} from '@remixicon/react';
import Link from "next/link";
import { Tooltip } from "@/app/components/components";

export function ModelSelectForm({models}: {models: ModelData[]}) {

    const [modelData, setModelData] = useState(models[0]);
    const params = useParams();

    useEffect(() => {
        if (params.model_id) {
            console.log(`ModelSelectForm: Setting model data from URL: ${params.model_id}`);
            const model_id = params.model_id as string;
            if (models.length > 0) {
                const selectedModel = models.find((model) => model.model_id === model_id);
                if (selectedModel) {
                    setModelData(selectedModel);
                }
            }
        }
    }, [params.model_id, models]);

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
            <form className="w-full">
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
                            <Tooltip content="Location">
                                <span className="flex items-center">
                                    <RiHome4Line className="mr-2" />
                                </span>
                            </Tooltip>
                            <span>{modelData.location}</span>
                        </ListItem>

                        <ListItem key="roof_incl">
                            <Tooltip content="Roof inclination">
                                <span className="flex items-center">
                                    <RiArrowUpWideLine className="mr-2" />
                                </span>
                            </Tooltip>
                            <span>{modelData.roof_incl}°</span>
                        </ListItem>

                        <ListItem key="roof_azimuth">
                            <Tooltip content="Roof orientation">
                                <span className="flex items-center">
                                    <RiCompassLine className="mr-2" />
                                </span>
                            </Tooltip>
                            <span>{modelData.roof_azimuth}°</span>
                        </ListItem>

                        <ListItem key="electr_cons">
                            <Tooltip content="Annual electricity consumption">
                                <span className="flex items-center">
                                    <RiLightbulbFlashLine className="mr-2" />
                                </span>
                            </Tooltip>
                            <span>{modelData.electr_cons} kWh</span>
                        </ListItem>

                        <ListItem key="peak_power">
                            <Tooltip content="PV peak power">
                                <span className="flex items-center">
                                    <RiSunLine className="mr-2" />
                                </span>
                            </Tooltip>
                            <span>{modelData.peak_power} kWp</span>
                        </ListItem>

                        <ListItem key="roof_azimuth">
                            <Tooltip content="Battery capacity">
                                <span className="flex items-center">
                                    <RiBattery2ChargeLine className="mr-2" />
                                </span>
                            </Tooltip>
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
