package com.bachata.ports;
import android.app.*;
import android.content.*;
import android.content.pm.ApplicationInfo;

public final class PortFactory extends AppComponentFactory {
    private AppComponentFactory original(ClassLoader c) {
        try { return (AppComponentFactory)c.loadClass("androidx.core.app.CoreComponentFactory")
                      .getDeclaredConstructor().newInstance(); }
        catch (Exception e) { throw new IllegalStateException("original Bachata factory",e); }
    }
    @Override public ClassLoader instantiateClassLoader(ClassLoader c, ApplicationInfo info) {
        PortBridge.hostInfo=info; PortBridge.hostLoader=c;
        return original(c).instantiateClassLoader(c,info);
    }
    @Override public Activity instantiateActivity(ClassLoader c,String name,Intent i)
        throws InstantiationException,IllegalAccessException,ClassNotFoundException {
        String kind=PortBridge.moduleKind(name);
        if(kind==null)return original(c).instantiateActivity(c,name,i);
        try { return (Activity)PortBridge.loader(kind,c).loadClass(name).getDeclaredConstructor().newInstance(); }
        catch(Exception e){ InstantiationException x=new InstantiationException("dedicated port: "+name);x.initCause(e);throw x; }
    }
    @Override public Application instantiateApplication(ClassLoader c,String n)
        throws InstantiationException,IllegalAccessException,ClassNotFoundException {
        return original(c).instantiateApplication(c,n);
    }
    @Override public Service instantiateService(ClassLoader c,String n,Intent i)
        throws InstantiationException,IllegalAccessException,ClassNotFoundException {
        return original(c).instantiateService(c,n,i);
    }
    @Override public BroadcastReceiver instantiateReceiver(ClassLoader c,String n,Intent i)
        throws InstantiationException,IllegalAccessException,ClassNotFoundException {
        return original(c).instantiateReceiver(c,n,i);
    }
    @Override public ContentProvider instantiateProvider(ClassLoader c,String n)
        throws InstantiationException,IllegalAccessException,ClassNotFoundException {
        return original(c).instantiateProvider(c,n);
    }
}
