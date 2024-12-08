import { Card, List, ListItem } from "@tremor/react";
import { ModelData } from "@/app/utils/definitions";
import { RiArrowUpWideLine, RiBattery2ChargeLine, RiCompassLine, RiHome4Line, RiInformationLine, RiLightbulbFlashLine, RiSunLine } from "@remixicon/react";
import { DeleteModelButton, GoToFinButton, RunSimButton, ViewSimButton } from "@/app/components/buttons";
import { Tooltip } from "@/app/components/components";

export async function ModelCard({modelData}: {modelData: ModelData}) {

    if (!modelData.model_id) {
        throw new Error('Model ID is not defined.');
    }

    let location_field: string;
    if (modelData.coordinates) {
        location_field = modelData.coordinates.display_name;
    } else {
        location_field = modelData.location;
    }

    return (
        <div className="p-2">
            <Card
                className="flex w-full lg:w-[70%] transition-all duration-300"
            >
                <div className="flex flex-col w-full items-center">
                    <h2 className="w-full text-center mb-1">{modelData.model_name}</h2>
                    <div className="flex flex-col md:flex-row w-full justify-between items-center">
                        <List className="p-2 w-[45%] mx-4">
                            <ListItem key="location" className="flex justify-between items-center">
                                <span className="flex items-center">
                                    <RiHome4Line className="mr-2" /> Location
                                </span>
                                <div className="flex items-center justify-end space-x-1 max-w-[50%]">
                                    <span className="truncate">
                                        {location_field}
                                    </span>
                                    <Tooltip content={location_field}>
                                        <RiInformationLine className="flex-shrink-0" />
                                    </Tooltip>
                                </div>
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
                        </List>
                        <List className="p-2 w-[45%] mx-4">
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
                            <ListItem key="roof_azimuth">
                                <span className="flex items-center">
                                    <RiBattery2ChargeLine className="mr-2" /> Battery capacity
                                </span>
                                <span>{modelData.battery_cap} kWh</span>
                            </ListItem>
                        </List>
                    </div>
                </div>
                <div className="flex flex-col justify-center mx-4 my-2">
                    {
                        modelData.sim_id
                            ?
                            <>
                                <ViewSimButton model_id={modelData.model_id} />
                                <GoToFinButton model_id={modelData.model_id} />
                            </>
                            : <RunSimButton model_id={modelData.model_id} />
                    }
                    <DeleteModelButton model_id={modelData.model_id}/>
                </div>
            </Card>
        </div>
    );
}
