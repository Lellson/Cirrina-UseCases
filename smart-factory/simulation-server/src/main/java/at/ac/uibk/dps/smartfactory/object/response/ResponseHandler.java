package at.ac.uibk.dps.smartfactory.object.response;

import at.ac.uibk.dps.smartfactory.object.variable.ContextVariable;

import java.util.List;
import java.util.Map;

/**
 * Response handler, takes a map (request body) and produces a list of context variables (response body).
 */
@FunctionalInterface
public interface ResponseHandler {
  List<ContextVariable> onHandle(Map<?, ?> in);
}
