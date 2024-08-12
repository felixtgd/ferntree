import { Card } from "@tremor/react";
import { ModelData } from "@/utils/definitions";

export async function ModelCard({modelData}: {modelData: ModelData}) {
    return (
        <div className="p-2">
            <Card
                className="flex flex-grow"
            >
                <h2>{modelData.model_name}</h2>
                <div className="flex flow-row">
                    <div className="p-2">
                        <p>Location: {modelData.location}</p>
                        <p>Roof inclination: {modelData.roof_incl}°</p>
                        <p>Roof azimuth: {modelData.roof_azimuth}°</p>
                    </div>
                    <div className="p-2">
                        <p>Electricity consumption: {modelData.electr_cons} kWh</p>
                        <p>Peak power: {modelData.peak_power} kWp</p>
                        <p>Battery capacity: {modelData.battery_cap} kWh</p>
                    </div>
                </div>
            </Card>
        </div>
    );
}
