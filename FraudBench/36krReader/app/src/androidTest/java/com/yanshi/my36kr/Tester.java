package com.yanshi.my36kr;

import android.support.test.uiautomator.By;
import android.support.test.uiautomator.UiDevice;
import android.support.test.uiautomator.UiObject2;
import android.support.test.uiautomator.Until;
import android.test.InstrumentationTestCase;

/**
 * Created by caochenhong on 16-5-19.
 */
public class Tester extends InstrumentationTestCase {
    private UiDevice device;

    @Override
    public void setUp() throws Exception{
        device = UiDevice.getInstance(getInstrumentation());
        device.pressHome();
        // Wait for the Apps icon to show up on the screen
        device.wait(Until.hasObject(By.desc("Apps")), 3000);
        UiObject2 appsButton = device.findObject(By.desc("Apps"));
        appsButton.click();
        // Wait for the Calculator icon to show up on the screen
        device.wait(Until.hasObject(By.text("36krReader")), 3000);
        UiObject2 testApp = device.findObject(By.text("36krReader"));
        testApp.click();

    }

    public void testAdd() throws Exception{
// Wait till the Calculator's buttons are on the screen
        device.wait(Until.hasObject(By.desc("Navigate up")), 3000);

// Select the button for nav
        UiObject2 navButton = device.findObject(By.desc("Navigate up"));
        navButton.click();
        device.wait(Until.hasObject(By.text("NEXT")), 3000);
// Select the button for +
        UiObject2 buttonNext = device.findObject(By.text("NEXT"));
        buttonNext.click();
//click the ad for three times
        device.wait(Until.hasObject(By.clazz("android.webkit.WebView")), 3000);
        UiObject2 adView = device.findObject(By.clazz("android.webkit.WebView"));
        adView.click();


        device.waitForIdle(3000);
        device.pressBack();

        device.wait(Until.hasObject(By.clazz("android.webkit.WebView")), 3000);
        UiObject2 adView1 = device.findObject(By.clazz("android.webkit.WebView"));
        adView1.click();


        device.waitForIdle(3000);
        device.waitForIdle(3000);
        device.pressBack();

        device.wait(Until.hasObject(By.clazz("android.webkit.WebView")), 3000);
        UiObject2 adView2 = device.findObject(By.clazz("android.webkit.WebView"));
        adView2.click();


        device.waitForIdle(3000);
        device.waitForIdle(3000);
        device.pressBack();

        device.wait(Until.hasObject(By.clazz("android.webkit.WebView")), 3000);
        UiObject2 adView3 = device.findObject(By.clazz("android.webkit.WebView"));
        adView3.click();


        device.waitForIdle(3000);
        device.waitForIdle(3000);
        device.pressBack();
    }

}
