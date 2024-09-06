import { Card, List, ListItem } from "@tremor/react";
import { ModelData } from "@/app/utils/definitions";
import { RiArrowUpWideLine, RiBattery2ChargeLine, RiCompassLine, RiHome4Line, RiLightbulbFlashLine, RiSunLine } from "@remixicon/react";
import { DeleteButton, RunButton, ViewButton } from "@/app/components/buttons";

export async function ModelCard({modelData}: {modelData: ModelData}) {

    if (!modelData.model_id) {
        throw new Error('Model ID is not defined.');
    }

    return (
        <div className="p-2">
            <Card
                className="flex w-full lg:w-[70%] transition-all duration-300"
            >
                <div className="flex flex-col w-full items-center">
                    <h2 className="w-full text-center mb-1">{modelData.model_name}</h2>
                    <div className="flex flex-col md:flex-row w-full">
                        <List className="p-2 w-full mx-4">
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
                                    <RiCompassLine className="mr-2" /> Roof azimuth
                                </span>
                                <span>{modelData.roof_azimuth}°</span>
                            </ListItem>
                        </List>
                        <List className="p-2 w-full mx-4">
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
                                <span>{modelData.peak_power} kW</span>
                            </ListItem>
                            <ListItem key="roof_azimuth">
                                <span className="flex items-center">
                                    <RiBattery2ChargeLine className="mr-2" /> Battery capacity
                                </span>
                                <span>{modelData.battery_cap} kWh</span>
                            </ListItem>
                        </List>
                    </div>
                </div>
                <div className="flex flex-col justify-center m-2">
                    {
                        modelData.sim_id
                            ? <ViewButton type="model" model_id={modelData.model_id} />
                            : <RunButton type="model" model_id={modelData.model_id} />
                    }
                    <DeleteButton type="model" model_id={modelData.model_id}/>
                </div>
            </Card>
        </div>
    );
}
