# Uptime Monitoring

SmartAPI routinely checks all registered OpenAPI V3 API metadata and checks that all endpoints specified are working as expected. Based on this check an **Uptime status** will be assigned (`pass`, `unknown`, `fail`). Swagger V2 metadata will be skipped and not tested and be assigned an Uptime status of `incompatible`.

## What happens during the uptime check?
Each compatible document in our registry will be loaded into a monitoring module that will test all method endpoints we are interested in.

Default status upon start: <img width="127" alt="Screen Shot 2022-04-27 at 11 14 26 AM" src="https://user-images.githubusercontent.com/23092057/165592597-ed266d5c-503d-4d8a-98a2-53c6dd2b7777.png">

At the end of the checks the final status is decided based on the collective results. While `pass` and `fail` statuses are more straight forward, `unknown` statuses can indicate a variety of issues. We try to give you some feedback in such case.

## What endpoints are tested?

Only endpoints that use **GET** or **POST** methods are tested.

## Are endpoint examples required?

Only if you specify them as such.  We can test a multiple combination of specifications, as long as you provide the appropriate requirements.
* For `GET` endpoints they may or may not need parameters
* For `POST` endpoints they may or may not need parameters/request body.

## Can I modify my specification in order to skip a specific endpoint?

In some instances there may be an endpoint that requires a parameter that is dynamically generated (eg. async IDs) or you are unable to provide for some reason. For this kind of instances you can mark the parameter or body as **required** and **NOT** provide it. This particular scenario is skipped and it will not interfere with the overall score _as long as other endpoints **pass**_.

## What if my endpoint works but takes a long time to respond?

We have a timeout setting of `30s`, if you believe that this will be an issue you can consider finding a faster example or follow our instructions to trigger a **skip** action as detailed above.

## What statuses can you expect from an OpenAPI V3 registered item?

* <img width="127" alt="Screen Shot 2022-04-27 at 11 14 26 AM" src="https://user-images.githubusercontent.com/23092057/165592597-ed266d5c-503d-4d8a-98a2-53c6dd2b7777.png"> If any endpoint required a body or parameters and they were not included as examples, or providing an untestable endpoint eg. specified but not implemented.
* <img width="100" alt="Screen Shot 2022-04-27 at 11 15 44 AM" src="https://user-images.githubusercontent.com/23092057/165592694-a2ae7c78-c8a8-4a89-8b72-1cfba5b836ec.png"> One or more endpoints respond with a status code other than `200`.
* <img width="103" alt="Screen Shot 2022-04-27 at 11 14 20 AM" src="https://user-images.githubusercontent.com/23092057/165592509-ddd6fe88-9b41-41d7-8bea-5f07066074cc.png"> Endpoints respond with success status codes of `200`.

## How is the overall status calculated?

🟢 = OK , 🟠 = Skipped/Issue , 🔴 = Failed

* <img width="127" alt="Screen Shot 2022-04-27 at 11 14 26 AM" src="https://user-images.githubusercontent.com/23092057/165592597-ed266d5c-503d-4d8a-98a2-53c6dd2b7777.png"> [🟠 ,🟠 , 🟠, 🟠, 🟠] If no OK's and all skipped or issues present.
* <img width="100" alt="Screen Shot 2022-04-27 at 11 15 44 AM" src="https://user-images.githubusercontent.com/23092057/165592694-a2ae7c78-c8a8-4a89-8b72-1cfba5b836ec.png"> [🟢 ,🟢 ,🔴, 🟠, 🟠, 🟠] If any failed endpoints.
* <img width="103" alt="Screen Shot 2022-04-27 at 11 14 20 AM" src="https://user-images.githubusercontent.com/23092057/165592509-ddd6fe88-9b41-41d7-8bea-5f07066074cc.png"> [🟢 ,🟢 , 🟠, 🟠, 🟠] No failing endpoints and at least one OK.


## What statuses can you expect from a Swagger V2 registered item?

* <img width="154" alt="Screen Shot 2022-05-03 at 12 47 05 PM" src="https://user-images.githubusercontent.com/23092057/166554417-ebf1c495-458d-4474-8703-66baa4991ce3.png"> This item simply will not be tested.  You can upgrade your metadata following this [guide](https://smart-api.info/guide).

## Is there any way to find out what went wrong for a status other than `PASS`?

Clicking on the badge itself will display a description of what each status means in addition to a message indicating what endpoint failed and the error type when possible.  Due to the wide variety of possibilities it's possible some issues cannot be captured to give back to the user.  If you experience something like this please let us know. 

***
Example of issue hint:
<img width="349" alt="Screen Shot 2022-05-12 at 6 53 16 AM" src="https://user-images.githubusercontent.com/23092057/168091363-0cb87bc0-7f49-4475-82cd-f2450c5d404a.png">

***

## How often are these checks performed?

SmartAPI will automatically check uptime daily.

## Can I refresh my status manually after updating my metadata?

Log in and navigate to your dashboard, click on the purple button to trigger a check, your uptime status will be reassigned. It's important to wait while this check happens, depending on the number of endpoints this may take longer.  Your report will be presented to you when it's done.
<img width="375" alt="Screen Shot 2022-04-27 at 12 26 52 PM" src="https://user-images.githubusercontent.com/23092057/165604619-321e8128-cfe8-47ff-a253-ad79dacd18f1.png">
