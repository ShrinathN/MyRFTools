#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"

void Error_Handler(void);

#define LED_Pin GPIO_PIN_13
#define LED_GPIO_Port GPIOC
#define RX_Pin GPIO_PIN_0
#define RX_GPIO_Port GPIOA


//macros

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
