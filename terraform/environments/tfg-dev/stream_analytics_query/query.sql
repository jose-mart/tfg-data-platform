SELECT 
    [sensor_de].[meetpunt_de].[Rijstrook] AS [Lane_ref],
    [sensor_de].[meetpunt_de].[lengtegraad_EPSG_4326] AS [Longitude],
    [sensor_de].[meetpunt_de].[breedtegraad_EPSG_4326] AS [Latitude],
    [sensor_da].[meetpunt_da].[@beschrijvende_id] AS [Descriptive_id],
    [sensor_da].[meetpunt_da].[@unieke_id] AS [sensor_id],
    [sensor_da].[meetpunt_da].[tijd_laatst_gewijzigd] AS [Update_time],
    [sensor_da].[meetpunt_da].[actueel_publicatie] AS [Update_rate],
    [sensor_da].[meetpunt_da].[beschikbaar] AS [Availability],
    [sensor_da].[meetpunt_da].[defect] AS [Failure_status],
    [sensor_da].[meetpunt_da].[geldig] AS [Data_regularity],
    [sensor_da].[miv].[tijd_publicatie] AS [Last_update]
INTO
    [sensor-status]
FROM (
    SELECT 
        [sde].*,
        [meetpuntAlias_de].[ArrayValue] as [MeetPunt_de]
    FROM
        [sensor-description] as sde
    CROSS APPLY GetArrayElements(mivconfig.meetpunt) AS [meetpuntAlias_de]
) as sensor_de
JOIN (
SELECT
        [sda].*,
        [meetpuntAlias_da].[ArrayValue] as [meetpunt_da]
    FROM
        [sensor-data] as sda
    CROSS APPLY GetArrayElements(miv.meetpunt) AS [meetpuntAlias_da]
) as sensor_da
ON
    [sensor_de].[meetpunt_de].[@unieke_id] = [sensor_da].[meetpunt_da].[@unieke_id]
AND
    [sensor_de].[meetpunt_de].[beschrijvende_id] = [sensor_da].[meetpunt_da].[@beschrijvende_id]
AND
    DATEDIFF(minute, sensor_da, sensor_de) BETWEEN 0 AND 2
WHERE 
    [sensor_de].[meetpunt_de].[Rijstrook] IS NOT NULL AND
    [sensor_de].[meetpunt_de].[lengtegraad_EPSG_4326] IS NOT NULL AND
    [sensor_de].[meetpunt_de].[breedtegraad_EPSG_4326] IS NOT NULL AND
    [sensor_da].[meetpunt_da].[@beschrijvende_id] IS NOT NULL AND
    [sensor_da].[meetpunt_da].[@unieke_id] IS NOT NULL AND
    [sensor_da].[meetpunt_da].[tijd_laatst_gewijzigd] IS NOT NULL AND
    [sensor_da].[meetpunt_da].[actueel_publicatie] IS NOT NULL AND
    [sensor_da].[meetpunt_da].[beschikbaar] IS NOT NULL AND
    [sensor_da].[meetpunt_da].[defect] IS NOT NULL AND
    [sensor_da].[meetpunt_da].[geldig] IS NOT NULL AND
    [sensor_da].[miv].[tijd_publicatie] IS NOT NULL


SELECT 
    [sensor_da].[meetpunt_da].[@beschrijvende_id] AS [Descriptive_id],
    [sensor_da].[meetpunt_da].[@unieke_id] AS [sensor_id],
    [sensor_de].[meetpunt_de].[Rijstrook] AS [Lane_ref],
    [sensor_de].[meetpunt_de].[lengtegraad_EPSG_4326] AS [Longitude],
    [sensor_de].[meetpunt_de].[breedtegraad_EPSG_4326] AS [Latitude],
    DATEPART(hour, [sensor_da].[miv].[tijd_publicatie]) AS [hour],
    AVG([sensor_da].[meetdata_da].[verkeersintensiteit]) AS [Total_vehicles],
    AVG([dbo].[avg_vehicles]) AS [avg_weekly],
    (AVG([sensor_da].[meetdata_da].[verkeersintensiteit]) - AVG([dbo].[avg_vehicles])) AS [traffic_status] 
INTO
    [traffic-status]
FROM (
    SELECT
        [sda].*,
        [meetpuntAlias_da].[ArrayValue] as [meetpunt_da],
        [meetdataAlias_da].[ArrayValue] as [meetdata_da]
    FROM
        [sensor-data] as sda
    CROSS APPLY GetArrayElements(miv.meetpunt) AS [meetpuntAlias_da]
    CROSS APPLY GetArrayElements([meetpuntAlias_da].[ArrayValue].[meetdata]) as [meetdataAlias_da]
) as sensor_da
JOIN (
    SELECT *
    FROM  [traffic-status-daily-processing]
) as dbo
ON
    [dbo].[sensor_id] = [sensor_da].[meetpunt_da].[@unieke_id]
AND
    [dbo].[descriptive_id] = [sensor_da].[meetpunt_da].[@beschrijvende_id]
JOIN
    (
        SELECT 
            [sde].*,
            [meetpuntAlias_de].[ArrayValue] as [MeetPunt_de]
        FROM
            [sensor-description] as sde
        CROSS APPLY GetArrayElements(mivconfig.meetpunt) AS [meetpuntAlias_de]
    ) as sensor_de
ON
    [sensor_de].[meetpunt_de].[@unieke_id] = [sensor_da].[meetpunt_da].[@unieke_id]
AND
    [sensor_de].[meetpunt_de].[beschrijvende_id] = [sensor_da].[meetpunt_da].[@beschrijvende_id]
AND
    DATEDIFF(minute, sensor_da, sensor_de) BETWEEN 0 AND 2
GROUP BY 
    TumblingWindow(minute, 1), 
    [sensor_da].[meetpunt_da].[@beschrijvende_id], 
    [sensor_da].[meetpunt_da].[@unieke_id],
    [sensor_de].[meetpunt_de].[Rijstrook],
    [sensor_de].[meetpunt_de].[lengtegraad_EPSG_4326],
    [sensor_de].[meetpunt_de].[breedtegraad_EPSG_4326],
    DATEPART(hour, [sensor_da].[miv].[tijd_publicatie])
HAVING
    [sensor_da].[meetpunt_da].[@beschrijvende_id] IS NOT NULL AND
    [sensor_da].[meetpunt_da].[@unieke_id] IS NOT NULL AND
    [sensor_de].[meetpunt_de].[Rijstrook] IS NOT NULL AND
    [sensor_de].[meetpunt_de].[lengtegraad_EPSG_4326] IS NOT NULL AND
    [sensor_de].[meetpunt_de].[breedtegraad_EPSG_4326] IS NOT NULL